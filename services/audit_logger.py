import datetime
from database.db import cursor, db

class AuditLogger:

    def log(self, request_id, event_type, stage, details):
        """
        Log to both file AND MySQL database
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # File mein log karo
        log_line = (
            f"\n{'='*60}\n"
            f"[{timestamp}]\n"
            f"Request ID  : {request_id}\n"
            f"Event       : {event_type}\n"
            f"Stage       : {stage}\n"
            f"Details     : {details}\n"
            f"{'='*60}"
        )

        with open("audit.log", "a") as f:
            f.write(log_line)

        # MySQL mein bhi log karo
        try:
            cursor.execute(
                """INSERT INTO audit_logs
                   (request_id, event_type, stage, details)
                   VALUES (%s, %s, %s, %s)""",
                (request_id, event_type, stage, str(details))
            )
            db.commit()
        except Exception as e:
            print(f"Audit DB log failed: {e}")

    def get_trail(self, request_id):
        """
        Kisi bhi request ka poora audit trail lo
        """
        try:
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