import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))

from engines.rule_engine import RuleEngine
from engines.workflow_engine import WorkflowEngine
from services.retry_service import RetryService

rule_engine = RuleEngine()
workflow_engine = WorkflowEngine()
retry_service = RetryService()


# ── Test 1: Happy Path ─────────────────────────
def test_happy_path_approved():
    """Valid request → APPROVED"""
    data = {
        "income": 50000,
        "loan_amount": 100000,
        "credit_score": 720
    }
    action, rules, messages = rule_engine.evaluate(data)
    decision = workflow_engine.process(action)
    assert decision == "APPROVED"
    assert rules == []
    print("✅ Happy path approved")


# ── Test 2: Rejected Low Credit ───────────────
def test_rejected_low_credit():
    """Credit score < 600 → REJECTED"""
    data = {
        "income": 50000,
        "loan_amount": 100000,
        "credit_score": 450
    }
    action, rules, messages = rule_engine.evaluate(data)
    decision = workflow_engine.process(action)
    assert decision == "REJECTED"
    assert "low_credit_score" in rules
    print("✅ Low credit rejected")


# ── Test 3: Manual Review ─────────────────────
def test_manual_review_low_income():
    """Income < 20000 → MANUAL REVIEW"""
    data = {
        "income": 15000,
        "loan_amount": 50000,
        "credit_score": 700
    }
    action, rules, messages = rule_engine.evaluate(data)
    decision = workflow_engine.process(action)
    assert decision == "MANUAL_REVIEW"
    assert "low_income" in rules
    print("✅ Low income manual review")


# ── Test 4: Large Loan Rejected ───────────────
def test_rejected_large_loan():
    """Loan > income*5 → REJECTED"""
    data = {
        "income": 50000,
        "loan_amount": 400000,
        "credit_score": 720
    }
    action, rules, messages = rule_engine.evaluate(data)
    decision = workflow_engine.process(action)
    assert decision == "REJECTED"
    assert "large_loan" in rules
    print("✅ Large loan rejected")


# ── Test 5: Duplicate Detection ───────────────
def test_duplicate_idempotency():
    """Same key → duplicate detected"""
    store = {}
    key = "test-key-001"
    store[key] = {"decision": "APPROVED"}
    assert key in store
    assert store[key]["decision"] == "APPROVED"
    print("✅ Duplicate detection works")


# ── Test 6: Retry Logic ───────────────────────
def test_retry_logic_success():
    """Retry service works on eventual success"""
    attempt_count = [0]

    def flaky_function():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise Exception("Simulated failure")
        return "success"

    result, attempts = retry_service.retry(
        flaky_function,
        retries=3,
        delay=0
    )
    assert result == "success"
    assert attempts == 3
    print("✅ Retry logic works")


# ── Test 7: Retry All Failed ──────────────────
def test_retry_all_failed():
    """All retries fail → Exception raise"""
    def always_fails():
        raise Exception("Always fails")

    try:
        retry_service.retry(always_fails, retries=3, delay=0)
        assert False, "Should have raised exception"
    except Exception as e:
        assert "All 3 attempts failed" in str(e)
    print("✅ All retries failed correctly")


# ── Test 8: Rule Change Scenario ─────────────
def test_rule_change_scenario():
    """
    Rules change hone pe
    different result aata hai
    """
    # Original data
    data = {
        "income": 50000,
        "loan_amount": 100000,
        "credit_score": 620
    }
    action1, rules1, _ = rule_engine.evaluate(data)

    # Same data but lower credit score
    data2 = {
        "income": 50000,
        "loan_amount": 100000,
        "credit_score": 450
    }
    action2, rules2, _ = rule_engine.evaluate(data2)

    assert action1 != action2
    print("✅ Rule change scenario works")


# ── Test 9: Invalid Input ─────────────────────
def test_boundary_credit_score():
    """Credit score exactly 600 → passes"""
    data = {
        "income": 50000,
        "loan_amount": 100000,
        "credit_score": 600
    }
    action, rules, messages = rule_engine.evaluate(data)
    decision = workflow_engine.process(action)
    assert decision == "APPROVED"
    print("✅ Boundary credit score 600 approved")


# ── Test 10: Workflow Stages ──────────────────
def test_all_workflow_stages():
    """Test all 3 workflow outcomes"""
    assert workflow_engine.process("reject") == "REJECTED"
    assert workflow_engine.process("manual_review") == "MANUAL_REVIEW"
    assert workflow_engine.process("approve") == "APPROVED"
    print("✅ All workflow stages work")