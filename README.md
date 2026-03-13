# ScoreMe Decision System 🏦

> Configurable Workflow Decision Platform
> Built for ScoreMe Hackathon 2026 | NIT Warangal

---

## 🎯 What is This?

An automated decision engine that processes
loan applications and returns instant decisions.

**Example:**
- Input  → Name, Income, Loan Amount, Credit Score
- Output → APPROVED / REJECTED / MANUAL REVIEW

---

## ✨ Key Features

- ✅ Configurable Rules (JSON — no code change needed)
- ✅ Idempotency (duplicate request prevention)
- ✅ Retry Logic (3x retry with exponential backoff)
- ✅ External API Simulation (Credit Bureau)
- ✅ Full Audit Trail (every action logged)
- ✅ MySQL Persistence
- ✅ Auto-generated API Docs (Swagger UI)

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.x | Programming Language |
| FastAPI | REST API Framework |
| MySQL | Database |
| Pydantic | Data Validation |
| Uvicorn | ASGI Server |
| Pytest | Testing |

---

## 📁 Project Structure
```
scoreme-decision-system/
│
├── app.py                    ← Main API (entry point)
│
├── config/
│   ├── rules.json            ← Business rules (configurable)
│   └── workflow.json         ← Workflow stages
│
├── engines/
│   ├── rule_engine.py        ← Rule evaluation logic
│   └── workflow_engine.py    ← Decision logic
│
├── services/
│   ├── external_service.py   ← Credit Bureau simulation
│   ├── retry_service.py      ← Retry with backoff
│   └── audit_logger.py       ← Audit trail logging
│
├── database/
│   └── db.py                 ← MySQL connection
│
├── tests/
│   └── test_system.py        ← 10 automated tests
│
├── README.md                 ← You are here
└── architecture.md           ← System design document
```

---

## ⚙️ Setup Instructions

### Step 1 — Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/scoreme-decision-system.git
cd scoreme-decision-system
```

### Step 2 — Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install Dependencies
```bash
pip install fastapi uvicorn mysql-connector-python pydantic pytest
```

### Step 4 — MySQL Setup
Open MySQL Workbench and run:
```sql
CREATE DATABASE scoreme_system;
USE scoreme_system;

CREATE TABLE requests (
    request_id VARCHAR(100),
    input_data TEXT,
    decision VARCHAR(50),
    rules_triggered TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(100),
    event_type VARCHAR(100),
    stage VARCHAR(100),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE idempotency_store (
    idempotency_key VARCHAR(255) PRIMARY KEY,
    request_id VARCHAR(100),
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 5 — Update Database Password
Edit `database/db.py`:
```python
password="YOUR_MYSQL_PASSWORD"
```

### Step 6 — Run Server
```bash
uvicorn app:app --reload
```

### Step 7 — Open API Docs
```
http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /process | Submit request → get decision |
| GET | /status/{id} | Check request status |
| GET | /audit/{id} | Full audit trail |
| GET | /history | All past requests |
| GET | /health | System health check |

---

## 📤 Example Request
```json
POST http://127.0.0.1:8000/process

{
  "name": "Satyam Kumar",
  "income": 50000,
  "loan_amount": 200000,
  "credit_score": 720,
  "idempotency_key": "satyam-loan-001"
}
```

## 📥 Example Response
```json
{
  "request_id": "abc-123-xyz",
  "decision": "APPROVED",
  "rules_triggered": [],
  "explanation": ["All rules passed successfully"],
  "credit_report": {
    "credit_grade": "B - Good",
    "report_id": "CR-45231"
  }
}
```

---

## 🔄 How Rules Work

Rules are defined in `config/rules.json`.

**To change a rule — just edit JSON:**
```json
{
  "name": "low_credit_score",
  "condition": "credit_score < 600",
  "action": "reject",
  "message": "Credit score below minimum"
}
```

**No code change needed! ✅**

---

## 🧪 Run Tests
```bash
pytest tests/test_system.py -v
```

Expected output:
```
test_happy_path_approved      PASSED ✅
test_rejected_low_credit      PASSED ✅
test_manual_review            PASSED ✅
test_rejected_large_loan      PASSED ✅
test_duplicate_idempotency    PASSED ✅
test_retry_logic_success      PASSED ✅
test_retry_all_failed         PASSED ✅
test_rule_change_scenario     PASSED ✅
test_boundary_credit_score    PASSED ✅
test_all_workflow_stages      PASSED ✅

10 passed ✅
```

---

## 🔒 Decision Examples

### Approved ✅
```
Input  : credit_score=720, income=50000
Rules  : All passed
Output : APPROVED
```

### Rejected ❌
```
Input  : credit_score=450, income=50000
Rules  : low_credit_score triggered
Output : REJECTED
Reason : Credit score below minimum threshold
```

### Manual Review ⚠️
```
Input  : credit_score=720, income=15000
Rules  : low_income triggered
Output : MANUAL_REVIEW
Reason : Income below minimum threshold
```

---

## 🚀 Live Demo
```
http://127.0.0.1:8000/docs
```

---

## 📧 Submission Details
```
Submitted by : Satyam Kumar
College      : NIT Warangal
Email        : it@scoreme.in
Subject      : assignment_nitwarangal_scoreme_[rollno]
```