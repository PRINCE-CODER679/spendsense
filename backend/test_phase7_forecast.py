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

def test_phase7_forecast():
    print("==================================================")
    print("RUNNING PHASE 7 SPENDING FORECAST TEST SUITE")
    print("==================================================")

    now = datetime.now()
    year = now.year
    month = now.month

    # 1. Health check
    code, health = request_json(f"{BASE_URL}/health")
    print(f"[PASS] Health Check: Status {code}, Result: {health}")
    assert health["status"] == "healthy", "Health check failed!"

    # 2. Get Forecast Summary
    code, summary = request_json(f"{BASE_URL}/api/insights/forecast/summary?year={year}&month={month}")
    print(f"[PASS] Forecast Summary Endpoint: Code {code}")
    print(f"   - Current Spend: ₹{summary['overall_current_spending']}")
    print(f"   - Projected Month-End: ₹{summary['overall_projected_spending']}")
    print(f"   - Daily Burn Rate: ₹{summary['daily_burn_rate']}/day")
    print(f"   - Days Elapsed: {summary['days_elapsed']}/{summary['days_in_month']}")
    print(f"   - High Risk Categories: {summary['high_risk_count']}")
    print(f"   - Moderate Risk Categories: {summary['moderate_risk_count']}")
    print(f"   - Total Predicted Overspend: ₹{summary['total_predicted_overspend']}")

    assert "overall_projected_spending" in summary
    assert "daily_burn_rate" in summary
    assert "category_forecasts" in summary

    # 3. Get Category Forecasts List
    code, categories = request_json(f"{BASE_URL}/api/insights/forecast/categories?year={year}&month={month}")
    print(f"[PASS] Category Forecasts Endpoint: Code {code}, Total Categories: {len(categories)}")
    
    for cat in categories:
        print(f"   - [{cat['risk_level'].upper()}] Category: {cat['category']} | Spent: ₹{cat['current_spending']} | Daily: ₹{cat['daily_rate']} | Projected: ₹{cat['projected_spending']} | Baseline: ₹{cat['historical_average']}")
        assert "category" in cat
        assert "projected_spending" in cat
        assert "daily_rate" in cat
        assert cat["risk_level"] in ["safe", "moderate_risk", "high_risk"]

    print("\n==================================================")
    print("ALL PHASE 7 FORECAST BACKEND TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_phase7_forecast()
