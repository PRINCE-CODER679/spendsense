from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.database.mongodb import mongodb
from app.services.projection_calculator import ProjectionCalculator
from app.services.trend_calculator import TrendCalculator, TrendDirection
from app.services.budget_service import budget_service


class InsightsService:
    """Service for generating spending insights from transaction data."""
    
    def __init__(self):
        self._collection = None
        self.overspending_threshold = 1.20  # 20% above historical average
        self.trend_threshold = 10.0  # 10% change threshold
        self.saving_opportunity_reduction = 0.15  # 15% reduction for opportunities
    
    @property
    def collection(self):
        if self._collection is None:
            self._collection = mongodb.get_database().transactions
        return self._collection
    
    async def get_category_spending_for_month(
        self, 
        user_id: str, 
        year: int, 
        month: int, 
        category: Optional[str] = None
    ) -> float:
        """Get total spending for a category in a specific month."""
        try:
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
            
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            return result[0]["total"] if result else 0.0
        except Exception as e:
            print(f"Warning: Insights DB error in get_category_spending_for_month: {e}")
            return 0.0
    
    async def get_historical_category_spending(
        self, 
        user_id: str, 
        category: str, 
        months: int = 6
    ) -> List[float]:
        """Get historical spending for a category over the past N months."""
        today = datetime.now()
        spending_values = []
        
        for i in range(1, months + 1):
            # Calculate month start and end
            month_date = today - timedelta(days=30 * i)
            year = month_date.year
            month = month_date.month
            
            spending = await self.get_category_spending_for_month(user_id, year, month, category)
            spending_values.append(spending)
        
        return spending_values
    
    async def get_monthly_income_expenses(
        self, 
        user_id: str, 
        year: int, 
        month: int
    ) -> Dict[str, float]:
        """Get total income and expenses for a specific month."""
        try:
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
            
            return {"income": income, "expenses": expenses}
        except Exception as e:
            print(f"Warning: Insights DB error in get_monthly_income_expenses: {e}")
            return {"income": 0.0, "expenses": 0.0}
    
    async def get_all_categories(self, user_id: str) -> List[str]:
        """Get all unique expense categories."""
        try:
            pipeline = [
                {"$match": {"user_id": user_id, "transaction_type": "expense"}},
                {"$group": {"_id": "$category"}},
                {"$sort": {"_id": 1}}
            ]
            
            results = await self.collection.aggregate(pipeline).to_list(length=None)
            return [result["_id"] for result in results]
        except Exception as e:
            print(f"Warning: Insights DB error in get_all_categories: {e}")
            return []
    
    async def generate_category_insights(
        self, 
        user_id: str, 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[Dict]:
        """Generate insights for each spending category."""
        if year is None or month is None:
            today = datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month

        categories = await self.get_all_categories(user_id)
        insights = []
        
        current_day = datetime.now().day
        
        for category in categories:
            current_spending = await self.get_category_spending_for_month(
                user_id, year, month, category
            )
            
            if current_spending == 0:
                continue
            
            # Calculate projection
            projection = ProjectionCalculator.calculate_category_projection(
                current_spending, year, month, current_day
            )
            
            # Get historical data
            historical_spending = await self.get_historical_category_spending(
                user_id, category, months=6
            )
            
            if not historical_spending or all(s == 0 for s in historical_spending):
                # Not enough historical data
                insights.append({
                    "type": "projection",
                    "severity": "info",
                    "category": category,
                    "title": f"{category} spending projection",
                    "message": f"You've spent ₹{current_spending:,.0f} on {category} so far this month.",
                    "value": current_spending,
                    "projected_value": projection["projected_spending"],
                    "has_historical_data": False
                })
                continue
            
            historical_average = TrendCalculator.calculate_historical_average(historical_spending)
            
            # Calculate trend
            trend_analysis = TrendCalculator.compare_with_multiple_periods(
                projection["projected_spending"],
                historical_spending,
                self.trend_threshold
            )
            
            # Check for overspending
            if projection["projected_spending"] > historical_average * self.overspending_threshold:
                difference = projection["projected_spending"] - historical_average
                insights.append({
                    "type": "overspending",
                    "severity": "warning",
                    "category": category,
                    "title": f"{category} spending is increasing",
                    "message": f"You're on track to spend ₹{projection['projected_spending']:,.0f} on {category} this month, approximately ₹{difference:,.0f} above your usual spending.",
                    "value": projection["projected_spending"],
                    "comparison_value": historical_average,
                    "percentage_above": ((difference / historical_average) * 100) if historical_average > 0 else 0
                })
            
            # Add trend insight
            if trend_analysis["trend"]["is_significant"]:
                direction = trend_analysis["trend"]["direction"]
                percentage = abs(trend_analysis["trend"]["percentage_change"])
                
                if direction == TrendDirection.INCREASING.value:
                    insights.append({
                        "type": "trend",
                        "severity": "warning",
                        "category": category,
                        "title": f"{category} spending increased",
                        "message": f"{category} spending increased {percentage:.0f}% compared with your previous period.",
                        "value": projection["projected_spending"],
                        "comparison_value": historical_average,
                        "percentage_change": percentage,
                        "direction": direction
                    })
                elif direction == TrendDirection.DECREASING.value:
                    insights.append({
                        "type": "trend",
                        "severity": "positive",
                        "category": category,
                        "title": f"{category} spending decreased",
                        "message": f"{category} spending decreased {percentage:.0f}% compared with your previous period.",
                        "value": projection["projected_spending"],
                        "comparison_value": historical_average,
                        "percentage_change": percentage,
                        "direction": direction
                    })
            
            # Add saving opportunity
            potential_savings = current_spending * self.saving_opportunity_reduction
            if potential_savings > 100:  # Only if savings > ₹100
                insights.append({
                    "type": "opportunity",
                    "severity": "info",
                    "category": category,
                    "title": f"{category} saving opportunity",
                    "message": f"Reducing {category} spending by {self.saving_opportunity_reduction * 100:.0f}% could save approximately ₹{potential_savings:,.0f} this month.",
                    "value": current_spending,
                    "potential_savings": potential_savings,
                    "reduction_percentage": self.saving_opportunity_reduction * 100
                })
        
        return insights
    
    async def generate_savings_insights(
        self, 
        user_id: str, 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[Dict]:
        """Generate savings-related insights."""
        if year is None or month is None:
            today = datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month

        current_month_data = await self.get_monthly_income_expenses(user_id, year, month)
        
        # Get previous month data
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1
        
        previous_month_data = await self.get_monthly_income_expenses(user_id, prev_year, prev_month)
        
        insights = []
        
        current_income = current_month_data["income"]
        current_expenses = current_month_data["expenses"]
        current_savings = current_income - current_expenses
        
        previous_income = previous_month_data["income"]
        previous_expenses = previous_month_data["expenses"]
        previous_savings = previous_income - previous_expenses
        
        # Calculate savings rate
        savings_rate = (current_savings / current_income * 100) if current_income > 0 else 0.0
        
        if current_income > 0:
            insights.append({
                "type": "savings",
                "severity": "info",
                "category": "savings",
                "title": "Current savings rate",
                "message": f"You're currently saving {savings_rate:.0f}% of your income.",
                "value": current_savings,
                "income": current_income,
                "expenses": current_expenses,
                "savings_rate": savings_rate
            })
        
        # Compare with previous month
        if previous_income > 0:
            savings_change = current_savings - previous_savings
            if savings_change != 0:
                change_type = "increased" if savings_change > 0 else "decreased"
                insights.append({
                    "type": "savings",
                    "severity": "positive" if savings_change > 0 else "warning",
                    "category": "savings",
                    "title": f"Savings {change_type}",
                    "message": f"Your savings {change_type} by ₹{abs(savings_change):,.0f} compared with last month.",
                    "value": current_savings,
                    "previous_value": previous_savings,
                    "change": savings_change
                })
        
        return insights
    
    async def generate_monthly_projection_insight(
        self, 
        user_id: str, 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> Optional[Dict]:
        """Generate overall monthly spending projection insight."""
        if year is None or month is None:
            today = datetime.now()
            year = today.year if year is None else year
            month = today.month if month is None else month
        current_spending = await self.get_category_spending_for_month(user_id, year, month)
        
        if current_spending == 0:
            return None
        
        current_day = datetime.now().day
        projection = ProjectionCalculator.calculate_category_projection(
            current_spending, year, month, current_day
        )
        
        return {
            "type": "projection",
            "severity": "info",
            "category": "overall",
            "title": "Monthly spending projection",
            "message": f"Based on your current spending rate, you're projected to spend ₹{projection['projected_spending']:,.0f} this month.",
            "value": current_spending,
            "projected_value": projection["projected_spending"],
            "days_elapsed": projection["days_elapsed"],
            "days_in_month": projection["days_in_month"]
        }
    
    async def generate_budget_insights(
        self, 
        user_id: str, 
        year: int, 
        month: int
    ) -> List[Dict]:
        """Generate budget-related insights."""
        budget_analysis = await budget_service.get_budget_analysis(user_id, year, month)
        insights = []
        
        current_day = datetime.now().day
        days_in_month = ProjectionCalculator.get_days_in_month(year, month)
        days_remaining = days_in_month - current_day
        
        # Overall budget insights
        if budget_analysis.get("overall_budget"):
            overall = budget_analysis["overall_budget"]
            if overall.is_over_budget:
                insights.append({
                    "type": "budget",
                    "severity": "warning",
                    "category": "overall",
                    "title": "Overall budget exceeded",
                    "message": f"You've exceeded your overall monthly budget by ₹{overall.over_budget_amount:,.0f}.",
                    "value": overall.actual_spending,
                    "budget_amount": overall.budget_amount,
                    "over_budget_amount": overall.over_budget_amount
                })
            elif overall.remaining > 0:
                insights.append({
                    "type": "budget",
                    "severity": "info",
                    "category": "overall",
                    "title": "Budget remaining",
                    "message": f"You have ₹{overall.remaining:,.0f} remaining from your overall monthly budget.",
                    "value": overall.actual_spending,
                    "budget_amount": overall.budget_amount,
                    "remaining": overall.remaining
                })
        
        # Category budget insights
        for category_budget in budget_analysis.get("category_budgets", []):
            category = category_budget.category
            if category_budget.is_over_budget:
                insights.append({
                    "type": "budget",
                    "severity": "warning",
                    "category": category,
                    "title": f"{category} budget exceeded",
                    "message": f"{category} has exceeded its monthly budget by ₹{category_budget.over_budget_amount:,.0f}.",
                    "value": category_budget.actual_spending,
                    "budget_amount": category_budget.budget_amount,
                    "over_budget_amount": category_budget.over_budget_amount
                })
            elif category_budget.status.value in ["warning", "near_limit"]:
                insights.append({
                    "type": "budget",
                    "severity": "warning",
                    "category": category,
                    "title": f"{category} budget warning",
                    "message": f"{category} budget is {category_budget.percentage_used:.0f}% used with {days_remaining} days remaining.",
                    "value": category_budget.actual_spending,
                    "budget_amount": category_budget.budget_amount,
                    "percentage_used": category_budget.percentage_used,
                    "days_remaining": days_remaining
                })
            
            # Budget-aware projection
            if category_budget.actual_spending > 0 and days_remaining > 0:
                current_spending = category_budget.actual_spending
                daily_rate = current_spending / current_day
                projected_total = current_spending + (daily_rate * days_remaining)
                
                if projected_total > category_budget.budget_amount:
                    projected_over = projected_total - category_budget.budget_amount
                    insights.append({
                        "type": "budget_projection",
                        "severity": "warning",
                        "category": category,
                        "title": f"{category} budget projection warning",
                        "message": f"At your current spending rate, you're projected to exceed your {category} budget by approximately ₹{projected_over:,.0f}.",
                        "value": current_spending,
                        "projected_value": projected_total,
                        "budget_amount": category_budget.budget_amount,
                        "projected_over": projected_over,
                        "daily_rate": daily_rate,
                        "days_remaining": days_remaining
                    })
        
        return insights
    
    async def generate_all_insights(
        self, 
        user_id: str = "default_user", 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Generate all insights for the user.
        
        Returns:
            {
                "summary": dict,
                "category_insights": list,
                "savings_insights": list,
                "projection": dict,
                "generated_at": str
            }
        """
        if year is None or month is None:
            today = datetime.now()
            year = today.year
            month = today.month
        
        # Generate category insights
        category_insights = await self.generate_category_insights(user_id, year, month)
        
        # Generate savings insights
        savings_insights = await self.generate_savings_insights(user_id, year, month)
        
        # Generate budget insights
        budget_insights = await self.generate_budget_insights(user_id, year, month)
        
        # Generate monthly projection
        projection = await self.generate_monthly_projection_insight(user_id, year, month)
        
        # Get summary data
        current_month_data = await self.get_monthly_income_expenses(user_id, year, month)
        
        return {
            "summary": {
                "income": current_month_data["income"],
                "expenses": current_month_data["expenses"],
                "savings": current_month_data["income"] - current_month_data["expenses"],
                "savings_rate": ((current_month_data["income"] - current_month_data["expenses"]) / current_month_data["income"] * 100) if current_month_data["income"] > 0 else 0.0
            },
            "category_insights": category_insights + budget_insights,
            "savings_insights": savings_insights,
            "projection": projection,
            "generated_at": datetime.now().isoformat(),
            "year": year,
            "month": month
        }


# Global insights service instance
insights_service = InsightsService()
