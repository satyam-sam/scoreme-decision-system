import json
import os

class RuleEngine:

    def __init__(self):
        path = os.path.join("config", "rules.json")
        with open(path) as f:
            self.rules = json.load(f)["rules"]

    def evaluate(self, data):
        triggered_rules = []
        messages = []

        for rule in self.rules:
            try:
                if eval(rule["condition"], {}, data):
                    triggered_rules.append(rule["name"])
                    messages.append(rule["message"])
                    return rule["action"], triggered_rules, messages
            except Exception:
                continue

        return "approve", triggered_rules, ["All rules passed"]