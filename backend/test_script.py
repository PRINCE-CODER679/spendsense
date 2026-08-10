import asyncio
import sys
from pathlib import Path

from app.database.mongodb import mongodb
from app.services.budget_service import budget_service
from app.services.insights_service import insights_service

async def main():
    print("Connecting to MongoDB Atlas...")
    await mongodb.connect()
    db = mongodb.get_database()
    print("Database connected:", db.name)
    
    # Check collections
    collections = await db.list_collection_names()
    print("Collections in database:", collections)
    
    # Check budgets collection
    budgets_count = await db.budgets.count_documents({})
    print(f"Total budget records: {budgets_count}")
    cursor = db.budgets.find({})
    async for b in cursor:
        b["_id"] = str(b["_id"])
        print("Budget doc:", b)
        
    # Check transactions collection
    tx_count = await db.transactions.count_documents({})
    print(f"Total transaction records: {tx_count}")
    
    # Test budget analysis
    analysis = await budget_service.get_budget_analysis()
    print("Budget analysis result:", analysis)

    # Test insights
    insights = await insights_service.generate_all_insights()
    print("Insights summary:", insights.get("summary"))
    print("Category insights count:", len(insights.get("category_insights", [])))
    print("Savings insights count:", len(insights.get("savings_insights", [])))

    await mongodb.close()

if __name__ == "__main__":
    asyncio.run(main())
