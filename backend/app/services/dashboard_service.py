from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.database.mongodb import mongodb
from app.schemas.transaction import TransactionType


class DashboardService:
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = mongodb.get_database().transactions
        return self._collection
    
    async def get_summary(self, user_id: str = "default_user", year: Optional[int] = None, month: Optional[int] = None) -> Dict:
        """Get financial summary for a specific month or all time."""
        query = {"user_id": user_id}
        
        # Filter by month if provided
        if year is not None and month is not None:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            query["date"] = {"$gte": start_date, "$lt": end_date}
        
        # Aggregate income and expenses
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$transaction_type",
                "total": {"$sum": "$amount"}
            }}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        
        total_income = 0.0
        total_expenses = 0.0
        
        for result in results:
            if result["_id"] == "income":
                total_income = result["total"]
            elif result["_id"] == "expense":
                total_expenses = result["total"]
        
        total_savings = total_income - total_expenses
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0.0
        
        # Get transaction count
        transaction_count = await self.collection.count_documents(query)
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "total_savings": total_savings,
            "savings_rate": round(savings_rate, 2),
            "transaction_count": transaction_count
        }
    
    async def get_category_spending(self, user_id: str = "default_user", year: Optional[int] = None, month: Optional[int] = None) -> Dict:
        """Get spending totals by category (expenses only)."""
        query = {
            "user_id": user_id,
            "transaction_type": "expense"
        }
        
        # Filter by month if provided
        if year is not None and month is not None:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            query["date"] = {"$gte": start_date, "$lt": end_date}
        
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"total": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        
        category_spending = {}
        for result in results:
            category_spending[result["_id"]] = result["total"]
        
        return category_spending
    
    async def get_monthly_trend(self, user_id: str = "default_user", months: int = 6) -> List[Dict]:
        """Get monthly income and expenses for the past N months."""
        today = datetime.utcnow()
        monthly_data = []
        
        for i in range(months - 1, -1, -1):
            # Calculate month start and end
            month_date = today - timedelta(days=30 * i)
            year = month_date.year
            month = month_date.month
            
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            query = {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lt": end_date}
            }
            
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$transaction_type",
                    "total": {"$sum": "$amount"}
                }}
            ]
            
            results = await self.collection.aggregate(pipeline).to_list(length=None)
            
            income = 0.0
            expenses = 0.0
            
            for result in results:
                if result["_id"] == "income":
                    income = result["total"]
                elif result["_id"] == "expense":
                    expenses = result["total"]
            
            month_name = start_date.strftime("%B")
            monthly_data.append({
                "month": month_name,
                "year": year,
                "income": income,
                "expenses": expenses
            })
        
        return monthly_data
    
    async def get_daily_spending(self, user_id: str = "default_user", year: Optional[int] = None, month: Optional[int] = None) -> List[Dict]:
        """Get daily expense totals for a specific month."""
        if year is None or month is None:
            today = datetime.utcnow()
            year = today.year
            month = today.month
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        query = {
            "user_id": user_id,
            "transaction_type": "expense",
            "date": {"$gte": start_date, "$lt": end_date}
        }
        
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                "amount": {"$sum": "$amount"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        
        daily_spending = []
        for result in results:
            daily_spending.append({
                "date": result["_id"],
                "amount": result["amount"]
            })
        
        return daily_spending
    
    async def get_top_categories(self, user_id: str = "default_user", year: Optional[int] = None, month: Optional[int] = None, limit: int = 5) -> List[Dict]:
        """Get top spending categories for a specific month."""
        category_spending = await self.get_category_spending(user_id, year, month)
        
        total_spending = sum(category_spending.values())
        
        # Sort by amount and get top categories
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        
        top_categories = []
        for category, amount in sorted_categories[:limit]:
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0.0
            top_categories.append({
                "category": category,
                "amount": amount,
                "percentage": round(percentage, 1)
            })
        
        return top_categories
    
    async def get_month_comparison(self, year: int, month: int, user_id: str = "default_user") -> Dict:
        """Compare current month expenses with previous month."""
        # Current month
        current_start = datetime(year, month, 1)
        if month == 12:
            current_end = datetime(year + 1, 1, 1)
        else:
            current_end = datetime(year, month + 1, 1)
        
        current_query = {
            "user_id": user_id,
            "transaction_type": "expense",
            "date": {"$gte": current_start, "$lt": current_end}
        }
        
        current_pipeline = [
            {"$match": current_query},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        current_result = await self.collection.aggregate(current_pipeline).to_list(length=1)
        current_expenses = current_result[0]["total"] if current_result else 0.0
        
        # Previous month
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1
        
        prev_start = datetime(prev_year, prev_month, 1)
        if prev_month == 12:
            prev_end = datetime(prev_year + 1, 1, 1)
        else:
            prev_end = datetime(prev_year, prev_month + 1, 1)
        
        prev_query = {
            "user_id": user_id,
            "transaction_type": "expense",
            "date": {"$gte": prev_start, "$lt": prev_end}
        }
        
        prev_pipeline = [
            {"$match": prev_query},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        prev_result = await self.collection.aggregate(prev_pipeline).to_list(length=1)
        prev_expenses = prev_result[0]["total"] if prev_result else 0.0
        
        # Calculate percentage change
        if prev_expenses > 0:
            percentage_change = ((current_expenses - prev_expenses) / prev_expenses) * 100
        else:
            percentage_change = 0.0 if current_expenses == 0 else 100.0
        
        return {
            "current_expenses": current_expenses,
            "previous_expenses": prev_expenses,
            "percentage_change": round(percentage_change, 1),
            "current_month_name": current_start.strftime("%B %Y"),
            "previous_month_name": prev_start.strftime("%B %Y")
        }


# Global dashboard service instance
dashboard_service = DashboardService()
