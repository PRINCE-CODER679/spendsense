import json
import sys
import urllib.request
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def request_json(url, method="GET", body=None):
    req = urllib.request.Request(url, method=method)
    if body:
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(body).encode('utf-8')
    else:
        data = None
    with urllib.request.urlopen(req, data=data, timeout=10) as resp:
        return resp.getcode(), json.loads(resp.read().decode('utf-8'))

def test_phase6_backend():
    print("==================================================")
    print("RUNNING COMPLETE PHASE 6 VERIFICATION TEST SUITE")
    print("==================================================")

    # 1. Health check
    code, health = request_json(f"{BASE_URL}/health")
    print(f"[✓] Health Check: Status {code}, Result: {health}")
    assert health["status"] == "healthy", "Health check failed!"

    current_year = datetime.now().year
    current_month = datetime.now().month

    # 2. Clean up any existing test budget for category 'Testing'
    code, budgets = request_json(f"{BASE_URL}/api/budgets?year={current_year}&month={current_month}")
    for b in budgets.get("budgets", []):
        if b.get("category") == "Testing":
            request_json(f"{BASE_URL}/api/budgets/{b['id']}", method="DELETE")
            print(f"[✓] Cleaned up previous test budget {b['id']}")

    # 3. Create a Category Budget
    create_payload = {
        "amount": 5000.0,
        "category": "Testing",
        "year": current_year,
        "month": current_month
    }
    code, created_budget = request_json(f"{BASE_URL}/api/budgets", method="POST", body=create_payload)
    print(f"[✓] Create Budget Response: Code {code}, ID: {created_budget['id']}")
    budget_id = created_budget["id"]
    assert created_budget["amount"] == 5000.0
    assert created_budget["category"] == "Testing"

    # 4. Get Budget by ID
    code, fetched_budget = request_json(f"{BASE_URL}/api/budgets/{budget_id}")
    print(f"[✓] Get Budget by ID: {fetched_budget['id']} matched")
    assert fetched_budget["id"] == budget_id

    # 5. Update Budget Amount
    update_payload = {"amount": 7500.0}
    code, updated_budget = request_json(f"{BASE_URL}/api/budgets/{budget_id}", method="PUT", body=update_payload)
    print(f"[✓] Update Budget: New Amount {updated_budget['amount']}")
    assert updated_budget["amount"] == 7500.0

    # 6. Budget Analysis API
    code, analysis = request_json(f"{BASE_URL}/api/budgets/analysis/current?year={current_year}&month={current_month}")
    print(f"[✓] Budget Analysis API: Found {len(analysis['category_budgets'])} category budgets")
    found_test = False
    for cb in analysis.get("category_budgets", []):
        if cb.get("category") == "Testing":
            found_test = True
            print(f"    - Testing Category Budget: Amount ₹{cb['budget_amount']}, Spent ₹{cb['actual_spending']}, Status '{cb['status']}', Utilization {cb['percentage_used']}%")
            assert cb["budget_amount"] == 7500.0
            assert cb["status"] in ["safe", "warning", "near_limit", "exceeded"]
    assert found_test, "Testing category budget not found in analysis!"

    # 7. Insights API Endpoint
    code, insights = request_json(f"{BASE_URL}/api/insights/?year={current_year}&month={current_month}")
    print(f"[✓] Insights API Engine: Generated successfully")
    print(f"    - Income: ₹{insights['summary']['income']}")
    print(f"    - Expenses: ₹{insights['summary']['expenses']}")
    print(f"    - Savings: ₹{insights['summary']['savings']}")
    print(f"    - Savings Rate: {insights['summary']['savings_rate']:.2f}%")
    print(f"    - Category Insights Count: {len(insights.get('category_insights', []))}")
    print(f"    - Savings Insights Count: {len(insights.get('savings_insights', []))}")
    if insights.get("projection"):
        print(f"    - Monthly Projection: ₹{insights['projection']['projected_value']}")

    # 8. Category Insights Endpoint
    code, cat_insights = request_json(f"{BASE_URL}/api/insights/category?year={current_year}&month={current_month}")
    print(f"[✓] Category Insights Endpoint: Code {code}")

    # 9. Savings Insights Endpoint
    code, sav_insights = request_json(f"{BASE_URL}/api/insights/savings?year={current_year}&month={current_month}")
    print(f"[✓] Savings Insights Endpoint: Code {code}")

    # 10. Projection Endpoint
    code, proj_insights = request_json(f"{BASE_URL}/api/insights/projection?year={current_year}&month={current_month}")
    print(f"[✓] Projection Insight Endpoint: Code {code}")

    # 11. Delete Test Budget
    code, del_resp = request_json(f"{BASE_URL}/api/budgets/{budget_id}", method="DELETE")
    print(f"[✓] Delete Budget Response: {del_resp}")

    print("\n==================================================")
    print("ALL PHASE 6 BACKEND & DB TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_phase6_backend()
