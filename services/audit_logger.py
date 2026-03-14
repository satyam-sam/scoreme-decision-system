import datetime
import os

class AuditLogger:

    def log(self, request_id, event_type, stage, details):

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_line = (
            f"\n{'='*60}\n"
            f"[{timestamp}]\n"
            f"Request ID : {request_id}\n"
            f"Event      : {event_type}\n"
            f"Stage      : {stage}\n"
            f"Details    : {details}\n"
            f"{'='*60}"
        )

        with open("audit.log", "a") as f:
            f.write(log_line)

    def get_trail(self, request_id):
        # DB connection lazy import
        try:
            from database.db import cursor
            cursor.execute(
                """SELECT event_type, stage, details, created_at
                   FROM audit_logs
                   WHERE request_id = %s
                   ORDER BY created_at ASC""",
                (request_id,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "event": r[0],
                    "stage": r[1],
                    "details": r[2],
                    "timestamp": str(r[3])
                }
                for r in rows
            ]
        except Exception as e:
            return []