import asyncio
import sys
from pathlib import Path

# Ensure backend path is in sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.database.mongodb import mongodb

client = TestClient(app)


async def run_verification():
    print("=" * 70)
    print("SPENDSENSE AI — MULTI-USER DATA ISOLATION VERIFICATION TEST")
    print("=" * 70)

    await mongodb.connect()

    # 1. Register User A and User B
    email_a = "user_alpha_test@example.com"
    email_b = "user_beta_test@example.com"
    password = "password123"

    print("\n1. Registering User A & User B...")
    res_a = client.post("/api/auth/register", json={"email": email_a, "password": password, "full_name": "User Alpha"})
    if res_a.status_code == 400 and "already registered" in res_a.text:
        res_a = client.post("/api/auth/login", json={"email": email_a, "password": password})
    
    assert res_a.status_code in (200, 201), f"User A auth failed: {res_a.text}"
    token_a = res_a.json()["access_token"]
    user_a_id = res_a.json()["user"]["id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"   ✓ User A authenticated. ID: {user_a_id}")

    res_b = client.post("/api/auth/register", json={"email": email_b, "password": password, "full_name": "User Beta"})
    if res_b.status_code == 400 and "already registered" in res_b.text:
        res_b = client.post("/api/auth/login", json={"email": email_b, "password": password})
    
    assert res_b.status_code in (200, 201), f"User B auth failed: {res_b.text}"
    token_b = res_b.json()["access_token"]
    user_b_id = res_b.json()["user"]["id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"   ✓ User B authenticated. ID: {user_b_id}")

    # 2. User A creates Transaction A and Budget A
    print("\n2. User A creating Transaction A & Budget A...")
    tx_a_payload = {
        "amount": 1500.0,
        "transaction_type": "expense",
        "description": "User A Laptop Stand",
        "category": "Shopping",
        "date": "2026-08-10T10:00:00"
    }
    res_tx_a = client.post("/api/transactions", json=tx_a_payload, headers=headers_a)
    assert res_tx_a.status_code == 201, f"Failed to create TX A: {res_tx_a.text}"
    tx_a_id = res_tx_a.json()["id"]
    print(f"   ✓ Transaction A created. ID: {tx_a_id}")

    budget_a_payload = {
        "amount": 2500.0,
        "category": "Shopping",
        "year": 2026,
        "month": 8
    }
    res_b_a = client.post("/api/budgets", json=budget_a_payload, headers=headers_a)
    assert res_b_a.status_code == 201, f"Failed to create Budget A: {res_b_a.text}"
    budget_a_id = res_b_a.json()["id"]
    print(f"   ✓ Budget A created. ID: {budget_a_id}")

    # 3. User B creates Transaction B and Budget B
    print("\n3. User B creating Transaction B & Budget B...")
    tx_b_payload = {
        "amount": 450.0,
        "transaction_type": "expense",
        "description": "User B Grocery Purchase",
        "category": "Food & Dining",
        "date": "2026-08-11T12:00:00"
    }
    res_tx_b = client.post("/api/transactions", json=tx_b_payload, headers=headers_b)
    assert res_tx_b.status_code == 201, f"Failed to create TX B: {res_tx_b.text}"
    tx_b_id = res_tx_b.json()["id"]
    print(f"   ✓ Transaction B created. ID: {tx_b_id}")

    budget_b_payload = {
        "amount": 800.0,
        "category": "Food & Dining",
        "year": 2026,
        "month": 8
    }
    res_b_b = client.post("/api/budgets", json=budget_b_payload, headers=headers_b)
    assert res_b_b.status_code == 201, f"Failed to create Budget B: {res_b_b.text}"
    budget_b_id = res_b_b.json()["id"]
    print(f"   ✓ Budget B created. ID: {budget_b_id}")

    # 4. Data Isolation Verification
    print("\n4. Verifying Data Isolation...")
    # User A fetching transactions
    tx_list_a = client.get("/api/transactions", headers=headers_a).json()["transactions"]
    tx_ids_a = [t["id"] for t in tx_list_a]
    assert tx_a_id in tx_ids_a, "User A should see Transaction A"
    assert tx_b_id not in tx_ids_a, "CRITICAL VULNERABILITY: User A can see User B's transaction!"
    print(f"   ✓ User A sees ONLY User A's transactions ({len(tx_list_a)} records found)")

    # User B fetching transactions
    tx_list_b = client.get("/api/transactions", headers=headers_b).json()["transactions"]
    tx_ids_b = [t["id"] for t in tx_list_b]
    assert tx_b_id in tx_ids_b, "User B should see Transaction B"
    assert tx_a_id not in tx_ids_b, "CRITICAL VULNERABILITY: User B can see User A's transaction!"
    print(f"   ✓ User B sees ONLY User B's transactions ({len(tx_list_b)} records found)")

    # User A fetching budgets
    b_list_a = client.get("/api/budgets", headers=headers_a).json()["budgets"]
    b_ids_a = [b["id"] for b in b_list_a]
    assert budget_a_id in b_ids_a, "User A should see Budget A"
    assert budget_b_id not in b_ids_a, "CRITICAL VULNERABILITY: User A can see User B's budget!"
    print(f"   ✓ User A sees ONLY User A's budgets ({len(b_list_a)} records found)")

    # User B fetching budgets
    b_list_b = client.get("/api/budgets", headers=headers_b).json()["budgets"]
    b_ids_b = [b["id"] for b in b_list_b]
    assert budget_b_id in b_ids_b, "User B should see Budget B"
    assert budget_a_id not in b_ids_b, "CRITICAL VULNERABILITY: User B can see User A's budget!"
    print(f"   ✓ User B sees ONLY User B's budgets ({len(b_list_b)} records found)")

    # 5. IDOR Security Prevention Test (User A targeting User B's resources)
    print("\n5. Running IDOR Security Prevention Attacks (User A -> User B's IDs)...")
    
    # GET Transaction B with User A's Token
    res_idor_get_tx = client.get(f"/api/transactions/{tx_b_id}", headers=headers_a)
    assert res_idor_get_tx.status_code == 404, f"IDOR Vulnerability! GET tx returned {res_idor_get_tx.status_code}"
    print("   ✓ GET /api/transactions/{tx_b_id} using Token A returned 404 Not Found")

    # PUT Transaction B with User A's Token
    res_idor_put_tx = client.put(f"/api/transactions/{tx_b_id}", json={"amount": 9999.0}, headers=headers_a)
    assert res_idor_put_tx.status_code == 404, f"IDOR Vulnerability! PUT tx returned {res_idor_put_tx.status_code}"
    print("   ✓ PUT /api/transactions/{tx_b_id} using Token A returned 404 Not Found")

    # DELETE Transaction B with User A's Token
    res_idor_del_tx = client.delete(f"/api/transactions/{tx_b_id}", headers=headers_a)
    assert res_idor_del_tx.status_code == 404, f"IDOR Vulnerability! DELETE tx returned {res_idor_del_tx.status_code}"
    print("   ✓ DELETE /api/transactions/{tx_b_id} using Token A returned 404 Not Found")

    # GET Budget B with User A's Token
    res_idor_get_b = client.get(f"/api/budgets/{budget_b_id}", headers=headers_a)
    assert res_idor_get_b.status_code == 404, f"IDOR Vulnerability! GET budget returned {res_idor_get_b.status_code}"
    print("   ✓ GET /api/budgets/{budget_b_id} using Token A returned 404 Not Found")

    # PUT Budget B with User A's Token
    res_idor_put_b = client.put(f"/api/budgets/{budget_b_id}", json={"amount": 9999.0}, headers=headers_a)
    assert res_idor_put_b.status_code == 404, f"IDOR Vulnerability! PUT budget returned {res_idor_put_b.status_code}"
    print("   ✓ PUT /api/budgets/{budget_b_id} using Token A returned 404 Not Found")

    # DELETE Budget B with User A's Token
    res_idor_del_b = client.delete(f"/api/budgets/{budget_b_id}", headers=headers_a)
    assert res_idor_del_b.status_code == 404, f"IDOR Vulnerability! DELETE budget returned {res_idor_del_b.status_code}"
    print("   ✓ DELETE /api/budgets/{budget_b_id} using Token A returned 404 Not Found")

    # 6. Dashboard & Analytics Isolation Verification
    print("\n6. Verifying Dashboard & Analytics Isolation...")
    dash_a = client.get("/api/dashboard/summary", headers=headers_a).json()
    dash_b = client.get("/api/dashboard/summary", headers=headers_b).json()
    
    assert dash_a["total_expenses"] == 1500.0, f"User A total expenses should be 1500.0, got {dash_a['total_expenses']}"
    assert dash_b["total_expenses"] == 450.0, f"User B total expenses should be 450.0, got {dash_b['total_expenses']}"
    print("   ✓ Dashboard summaries isolated (User A: $1500 expense vs User B: $450 expense)")

    # 7. AI Assistant Context Isolation Verification
    print("\n7. Verifying AI Assistant Financial Context Isolation...")
    ai_res_a = client.post("/api/assistant/chat", json={"message": "What are my expenses?"}, headers=headers_a).json()
    ai_res_b = client.post("/api/assistant/chat", json={"message": "What are my expenses?"}, headers=headers_b).json()

    assert "Laptop Stand" in ai_res_a["reply"] or "1,500" in ai_res_a["reply"] or "Shopping" in ai_res_a["reply"], "AI Assistant should reference User A's data for User A"
    assert "Grocery" in ai_res_b["reply"] or "450" in ai_res_b["reply"] or "Food" in ai_res_b["reply"], "AI Assistant should reference User B's data for User B"
    print("   ✓ AI Assistant financial context isolated per authenticated user")

    print("\n" + "=" * 70)
    print("ALL MULTI-USER ISOLATION TESTS PASSED 100% SUCCESSFULLY!")
    print("=" * 70)

    await mongodb.close()


if __name__ == "__main__":
    asyncio.run(run_verification())
