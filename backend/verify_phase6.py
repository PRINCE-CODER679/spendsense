import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8')
    else:
        body = None
    
    try:
        with urllib.request.urlopen(req, data=body, timeout=5) as resp:
            status = resp.getcode()
            res_data = json.loads(resp.read().decode('utf-8'))
            print(f"[PASS] {name} ({method} {path}) -> Status {status}")
            return res_data
    except Exception as e:
        print(f"[INFO/DEGRADED] {name} ({method} {path}) -> {e}")
        return None

def main():
    print("==================================================")
    print("VERIFYING PHASE 6 API ENDPOINTS")
    print("==================================================")
    
    # 1. Health check
    test_endpoint("Health Check", "/health")
    
    # 2. Budget Analysis
    analysis = test_endpoint("Budget Analysis", "/api/budgets/analysis/current")
    if analysis:
        print("   Budget Analysis result keys:", list(analysis.keys()))
        
    # 3. Get Budgets
    budgets = test_endpoint("Get Budgets List", "/api/budgets")
    if budgets:
        print("   Budgets Total:", budgets.get("total"))
        
    # 4. Insights API
    insights = test_endpoint("All Insights Engine", "/api/insights/")
    if insights:
        print("   Category Insights count:", len(insights.get("category_insights", [])))
        print("   Savings Insights count:", len(insights.get("savings_insights", [])))
        
    # 5. Category Insights
    test_endpoint("Category Insights Endpoint", "/api/insights/category")
    
    # 6. Savings Insights
    test_endpoint("Savings Insights Endpoint", "/api/insights/savings")
    
    # 7. Monthly Projection
    test_endpoint("Monthly Projection Endpoint", "/api/insights/projection")

if __name__ == "__main__":
    main()
