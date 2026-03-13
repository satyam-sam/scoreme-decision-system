import random
import time

class ExternalCreditService:
    """
    Simulates external Credit Bureau API
    Real life mein CIBIL/Experian API hoti hai
    """

    def get_credit_report(self, applicant_name, credit_score):

        # Simulate network delay (0.5 to 2 seconds)
        time.sleep(random.uniform(0.5, 2.0))

        # Simulate 20% failure rate (realistic!)
        if random.random() < 0.2:
            raise Exception("Credit Bureau API timeout - Service unavailable")

        # Return enriched credit report
        return {
            "bureau": "SimulatedCreditBureau",
            "applicant": applicant_name,
            "credit_score": credit_score,
            "credit_grade": self._get_grade(credit_score),
            "default_history": credit_score < 600,
            "report_id": f"CR-{random.randint(10000, 99999)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_grade(self, score):
        if score >= 750:
            return "A - Excellent"
        elif score >= 700:
            return "B - Good"
        elif score >= 650:
            return "C - Fair"
        elif score >= 600:
            return "D - Poor"
        else:
            return "F - Very Poor"