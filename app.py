from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import json

from engines.rule_engine import RuleEngine
from engines.workflow_engine import WorkflowEngine
from services.audit_logger import AuditLogger
from services.retry_service import RetryService
from services.external_service import ExternalCreditService
from database.db import cursor, db

app = FastAPI(
    title="ScoreMe Decision System",
    description="Configurable Workflow Decision Platform",
    version="2.0.0"
)

# Initialize all services
rule_engine = RuleEngine()
workflow_engine = WorkflowEngine()
logger = AuditLogger()
retry_service = RetryService()
credit_service = ExternalCreditService()


class RequestModel(BaseModel):
    name: str
    income: int
    loan_amount: int
    credit_score: int
    idempotency_key: str = None  # Optional


# ─────────────────────────────────────────────
# POST /process — Main Decision Endpoint
# ─────────────────────────────────────────────
@app.post("/process")
def process_request(request: RequestModel):

    data = request.dict()
    idempotency_key = data.pop("idempotency_key", None)

    # ── STEP 1: Idempotency Check ──────────────
    if idempotency_key:
        try:
            cursor.execute(
                "SELECT request_id, response FROM idempotency_store WHERE idempotency_key = %s",
                (idempotency_key,)
            )
            existing = cursor.fetchone()
            if existing:
                return {
                    "duplicate": True,
                    "message": "Duplicate request — returning previous result",
                    "request_id": existing[0],
                    "previous_result": json.loads(existing[1])
                }
        except Exception as e:
            print(f"Idempotency check failed: {e}")

    # ── STEP 2: Create Request ID ──────────────
    request_id = str(uuid.uuid4())

    # ── STEP 3: Audit — Request Received ───────
    logger.log(
        request_id,
        "REQUEST_RECEIVED",
        "intake",
        f"Input: {data}"
    )

    # ── STEP 4: External Credit Bureau Call ────
    credit_report = None
    credit_attempts = 0

    try:
        credit_report, credit_attempts = retry_service.retry(
            func=lambda: credit_service.get_credit_report(
                data["name"],
                data["credit_score"]
            ),
            retries=3,
            delay=1
        )

        logger.log(
            request_id,
            "EXTERNAL_CALL_SUCCESS",
            "credit_check",
            f"Credit report fetched after {credit_attempts} attempt(s). "
            f"Grade: {credit_report['credit_grade']}"
        )

    except Exception as e:
        logger.log(
            request_id,
            "EXTERNAL_CALL_FAILED",
            "credit_check",
            f"Credit bureau failed after 3 retries: {str(e)}"
        )
        credit_report = {
            "bureau": "Unavailable",
            "credit_grade": "Unknown",
            "report_id": "N/A",
            "error": str(e)
        }

    # ── STEP 5: Rules Evaluation ───────────────
    logger.log(
        request_id,
        "RULES_EVALUATION_START",
        "rule_engine",
        f"Evaluating rules for: {data}"
    )

    action, rules_triggered, messages = rule_engine.evaluate(data)

    logger.log(
        request_id,
        "RULES_EVALUATION_DONE",
        "rule_engine",
        f"Action: {action} | Rules: {rules_triggered} | Messages: {messages}"
    )

    # ── STEP 6: Workflow Decision ──────────────
    decision = workflow_engine.process(action)

    logger.log(
        request_id,
        "DECISION_MADE",
        "workflow_engine",
        f"Final Decision: {decision}"
    )

    # ── STEP 7: Save to MySQL ──────────────────
    try:
        cursor.execute(
            """INSERT INTO requests
               (request_id, input_data, decision, rules_triggered)
               VALUES (%s, %s, %s, %s)""",
            (
                request_id,
                json.dumps(data),
                decision,
                json.dumps(rules_triggered)
            )
        )
        db.commit()

        logger.log(
            request_id,
            "STATE_SAVED",
            "database",
            f"Request saved to MySQL successfully"
        )

    except Exception as e:
        logger.log(
            request_id,
            "STATE_SAVE_FAILED",
            "database",
            f"MySQL save failed: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

    # ── STEP 8: Build Result ───────────────────
    result = {
        "request_id": request_id,
        "decision": decision,
        "rules_triggered": rules_triggered,
        "explanation": messages,
        "credit_report": credit_report,
        "input": data
    }

    # ── STEP 9: Save Idempotency Key ───────────
    if idempotency_key:
        try:
            cursor.execute(
                """INSERT INTO idempotency_store
                   (idempotency_key, request_id, response)
                   VALUES (%s, %s, %s)""",
                (
                    idempotency_key,
                    request_id,
                    json.dumps(result)
                )
            )
            db.commit()
        except Exception as e:
            print(f"Idempotency save failed: {e}")

    logger.log(
        request_id,
        "REQUEST_COMPLETED",
        "completed",
        f"Decision: {decision} | Rules: {rules_triggered}"
    )

    return result


# ─────────────────────────────────────────────
# GET /status/:id — Request Status
# ─────────────────────────────────────────────
@app.get("/status/{request_id}")
def get_status(request_id: str):
    cursor.execute(
        "SELECT * FROM requests WHERE request_id = %s",
        (request_id,)
    )
    row = cursor.fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )
    return {
        "request_id": row[0],
        "decision": row[2],
        "rules_triggered": json.loads(row[3] or "[]"),
        "created_at": str(row[4])
    }


# ─────────────────────────────────────────────
# GET /audit/:id — Full Audit Trail
# ─────────────────────────────────────────────
@app.get("/audit/{request_id}")
def get_audit_trail(request_id: str):
    trail = logger.get_trail(request_id)
    if not trail:
        raise HTTPException(
            status_code=404,
            detail="No audit trail found"
        )
    return {
        "request_id": request_id,
        "total_events": len(trail),
        "audit_trail": trail
    }


# ─────────────────────────────────────────────
# GET /history — All Requests
# ─────────────────────────────────────────────
@app.get("/history")
def get_history():
    cursor.execute(
        "SELECT request_id, decision, created_at FROM requests ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    return {
        "total": len(rows),
        "requests": [
            {
                "request_id": r[0],
                "decision": r[1],
                "created_at": str(r[2])
            }
            for r in rows
        ]
    }


# ─────────────────────────────────────────────
# GET /health — Health Check
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "services": {
            "api": "running",
            "database": "connected",
            "rule_engine": "active",
            "external_service": "simulated"
        }
    }