from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
from app.database.mongodb import mongodb
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetAnalysis, BudgetStatus


class BudgetService:
    """Service for budget management and analysis."""
    
    def __init__(self):
        self._collection = None
        self.safe_threshold = 0.70  # 70%
        self.warning_threshold = 0.90  # 90%
        self.near_limit_threshold = 1.0  # 100%
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = mongodb.get_database().budgets
        return self._collection
    
    async def create_budget(
        self, 
        budget_data: BudgetCreate, 
        user_id: str = "default_user"
    ) -> Dict:
        """Create a new budget."""
        # Check for duplicate budget
        query = {
            "user_id": user_id,
            "year": budget_data.year,
            "month": budget_data.month,
            "category": budget_data.category
        }
        
        existing = await self.collection.find_one(query)
        if existing:
            raise ValueError(f"Budget already exists for this category/month")
        
        budget_dict = {
            "user_id": user_id,
            "amount": budget_data.amount,
            "category": budget_data.category,
            "year": budget_data.year,
            "month": budget_data.month,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(budget_dict)
        budget_dict["id"] = str(result.inserted_id)
        
        return budget_dict
    
    async def get_budget(
        self, 
        budget_id: str, 
        user_id: str = "default_user"
    ) -> Optional[Dict]:
        """Get a budget by ID."""
        try:
            obj_id = ObjectId(budget_id)
        except:
            return None
        
        budget = await self.collection.find_one({
            "_id": obj_id,
            "user_id": user_id
        })
        
        if budget:
            budget["id"] = str(budget["_id"])
            del budget["_id"]
        
        return budget
    
    async def get_budgets(
        self, 
        user_id: str = "default_user",
        year: Optional[int] = None,
        month: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get budgets with optional filters."""
        query = {"user_id": user_id}
        
        if year is not None:
            query["year"] = year
        if month is not None:
            query["month"] = month
        if category is not None:
            query["category"] = category
        
        try:
            cursor = self.collection.find(query).sort("category", 1)
            budgets = []
            
            async for budget in cursor:
                budget["id"] = str(budget["_id"])
                del budget["_id"]
                budgets.append(budget)
            
            return budgets
        except Exception as e:
            print(f"Warning: Failed to fetch budgets from MongoDB: {e}")
            return []
    
    async def update_budget(
        self, 
        budget_id: str, 
        budget_data: BudgetUpdate, 
        user_id: str = "default_user"
    ) -> Optional[Dict]:
        """Update a budget."""
        try:
            obj_id = ObjectId(budget_id)
        except:
            return None
        
        update_dict = {
            "amount": budget_data.amount,
            "updated_at": datetime.utcnow()
        }
        
        try:
            result = await self.collection.update_one(
                {"_id": obj_id, "user_id": user_id},
                {"$set": update_dict}
            )
            
            if result.matched_count > 0 or result.modified_count > 0:
                return await self.get_budget(budget_id, user_id)
        except Exception as e:
            print(f"Warning: Failed to update budget: {e}")
        
        return None
    
    async def delete_budget(
        self, 
        budget_id: str, 
        user_id: str = "default_user"
    ) -> bool:
        """Delete a budget."""
        try:
            obj_id = ObjectId(budget_id)
        except:
            return False
        
        try:
            result = await self.collection.delete_one({
                "_id": obj_id,
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Warning: Failed to delete budget: {e}")
            return False
    
    async def get_category_spending(
        self, 
        user_id: str, 
        year: int, 
        month: int, 
        category: Optional[str] = None
    ) -> float:
        """Get total spending for a category in a specific month."""
        try:
            transactions = mongodb.get_database().transactions
            
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
            
            if category:
                query["category"] = category
            
            pipeline = [
                {"$match": query},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            
            result = await transactions.aggregate(pipeline).to_list(length=1)
            return result[0]["total"] if result else 0.0
        except Exception as e:
            print(f"Warning: Failed to get category spending: {e}")
            return 0.0
    
    def calculate_budget_status(
        self, 
        percentage_used: float
    ) -> BudgetStatus:
        """Calculate budget status based on percentage used."""
        if percentage_used >= self.near_limit_threshold:
            return BudgetStatus.EXCEEDED
        elif percentage_used >= self.warning_threshold:
            return BudgetStatus.NEAR_LIMIT
        elif percentage_used >= self.safe_threshold:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.SAFE
    
    async def analyze_budget(
        self, 
        budget: Dict, 
        user_id: str = "default_user"
    ) -> BudgetAnalysis:
        """Analyze budget vs actual spending."""
        actual_spending = await self.get_category_spending(
            user_id,
            budget["year"],
            budget["month"],
            budget["category"]
        )
        
        budget_amount = budget["amount"]
        remaining = budget_amount - actual_spending
        percentage_used = (actual_spending / budget_amount * 100) if budget_amount > 0 else 0
        is_over_budget = actual_spending > budget_amount
        over_budget_amount = actual_spending - budget_amount if is_over_budget else 0
        
        status = self.calculate_budget_status(percentage_used / 100)
        
        return BudgetAnalysis(
            budget_id=budget["id"],
            category=budget["category"],
            budget_amount=budget_amount,
            actual_spending=actual_spending,
            remaining=remaining,
            percentage_used=round(percentage_used, 2),
            is_over_budget=is_over_budget,
            over_budget_amount=round(over_budget_amount, 2),
            status=status,
            year=budget["year"],
            month=budget["month"]
        )
    
    async def get_budget_analysis(
        self, 
        user_id: str = "default_user",
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> Dict:
        """Get comprehensive budget analysis."""
        if year is None or month is None:
            today = datetime.now()
            year = today.year
            month = today.month
        
        budgets = await self.get_budgets(user_id, year, month)
        
        overall_budget = None
        category_budgets = []
        
        for budget in budgets:
            analysis = await self.analyze_budget(budget, user_id)
            
            if budget["category"] is None:
                overall_budget = analysis
            else:
                category_budgets.append(analysis)
        
        return {
            "overall_budget": overall_budget,
            "category_budgets": category_budgets,
            "year": year,
            "month": month
        }


# Global budget service instance
budget_service = BudgetService()
