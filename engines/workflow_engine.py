class WorkflowEngine:

    def process(self, action):

        if action == "reject":
            return "REJECTED"

        elif action == "manual_review":
            return "MANUAL_REVIEW"

        else:
            return "APPROVED"