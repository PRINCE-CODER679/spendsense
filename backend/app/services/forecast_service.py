from typing import Dict, List, Optional
from datetime import datetime
from app.services.projection_calculator import ProjectionCalculator
from app.services.trend_calculator import TrendCalculator
from app.services.insights_service import insights_service
from app.services.budget_service import budget_service
from app.schemas.forecast import CategoryForecast, ForecastSummary


class ForecastService:
    """Service for generating structured spending forecasts and budget predictions."""
    
    async def get_category_forecasts(
        self, 
        user_id: str = "default_user", 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> List[CategoryForecast]:
        """Calculate spending forecasts and risk levels for all expense categories."""
        today = datetime.now()
        year = today.year if year is None else year
        month = today.month if month is None else month
        current_day = today.day if (year == today.year and month == today.month) else ProjectionCalculator.get_days_in_month(year, month)
        
        categories = await insights_service.get_all_categories(user_id)
        existing_budgets = await budget_service.get_budgets(user_id, year=year, month=month)
        budget_map = {b["category"]: b["amount"] for b in existing_budgets}
        
        forecasts = []
        
        for category in categories:
            current_spending = await insights_service.get_category_spending_for_month(
                user_id, year, month, category
            )
            
            if current_spending == 0 and category not in budget_map:
                continue
            
            projection = ProjectionCalculator.calculate_category_projection(
                current_spending, year, month, current_day
            )
            
            historical_spending = await insights_service.get_historical_category_spending(
                user_id, category, months=6
            )
            historical_avg = TrendCalculator.calculate_historical_average(historical_spending)
            
            budget_amount = budget_map.get(category)
            baseline = budget_amount if budget_amount is not None and budget_amount > 0 else historical_avg
            
            projected_spending = projection["projected_spending"]
            daily_rate = projection["daily_rate"]
            
            projected_overspend = 0.0
            percentage_above = 0.0
            
            if baseline > 0:
                if projected_spending > baseline:
                    projected_overspend = round(projected_spending - baseline, 2)
                    percentage_above = round(((projected_spending - baseline) / baseline) * 100, 2)
            
            # Risk Level Assessment
            if budget_amount is not None and budget_amount > 0:
                if projected_spending > budget_amount * 1.10:
                    risk_level = "high_risk"
                elif projected_spending > budget_amount:
                    risk_level = "moderate_risk"
                else:
                    risk_level = "safe"
            elif historical_avg > 0:
                if projected_spending > historical_avg * 1.25:
                    risk_level = "high_risk"
                elif projected_spending > historical_avg * 1.10:
                    risk_level = "moderate_risk"
                else:
                    risk_level = "safe"
            else:
                risk_level = "safe"
            
            # Trend calculation
            trend_info = TrendCalculator.calculate_trend(projected_spending, historical_avg)
            
            days_in_month = ProjectionCalculator.get_days_in_month(year, month)
            days_remaining = max(0, days_in_month - current_day)
            if current_day <= 2:
                confidence = "low"
            elif current_day <= 5:
                confidence = "medium"
            else:
                confidence = "high"

            forecasts.append(CategoryForecast(
                category=category,
                current_spending=round(current_spending, 2),
                daily_rate=daily_rate,
                projected_spending=projected_spending,
                historical_average=historical_avg,
                budget_amount=budget_amount,
                projected_overspend=projected_overspend,
                risk_level=risk_level,
                trend_direction=trend_info["direction"],
                percentage_above_baseline=percentage_above,
                confidence_level=confidence,
                days_remaining=days_remaining
            ))
            
        # Sort forecasts by risk level (high_risk first) then projected spending descending
        risk_order = {"high_risk": 0, "moderate_risk": 1, "safe": 2}
        forecasts.sort(key=lambda f: (risk_order.get(f.risk_level, 2), -f.projected_spending))
        
        return forecasts
    
    async def get_forecast_summary(
        self, 
        user_id: str = "default_user", 
        year: Optional[int] = None, 
        month: Optional[int] = None
    ) -> ForecastSummary:
        """Generate complete monthly forecast summary and risk matrix."""
        today = datetime.now()
        year = today.year if year is None else year
        month = today.month if month is None else month
        days_in_month = ProjectionCalculator.get_days_in_month(year, month)
        days_elapsed = min(today.day, days_in_month) if (year == today.year and month == today.month) else days_in_month
        days_remaining = max(0, days_in_month - days_elapsed)

        if days_elapsed <= 2:
            confidence = "low"
        elif days_elapsed <= 5:
            confidence = "medium"
        else:
            confidence = "high"
        
        overall_current = await insights_service.get_category_spending_for_month(user_id, year, month)
        overall_projected = ProjectionCalculator.calculate_monthly_projection(
            overall_current, days_elapsed, days_in_month
        )
        
        daily_burn_rate = round((overall_current / days_elapsed), 2) if days_elapsed > 0 else 0.0
        
        category_forecasts = await self.get_category_forecasts(user_id, year, month)
        
        high_risk_count = sum(1 for f in category_forecasts if f.risk_level == "high_risk")
        moderate_risk_count = sum(1 for f in category_forecasts if f.risk_level == "moderate_risk")
        total_predicted_overspend = round(sum(f.projected_overspend for f in category_forecasts), 2)
        
        return ForecastSummary(
            overall_current_spending=round(overall_current, 2),
            overall_projected_spending=overall_projected,
            days_elapsed=days_elapsed,
            days_in_month=days_in_month,
            days_remaining=days_remaining,
            confidence_level=confidence,
            daily_burn_rate=daily_burn_rate,
            high_risk_count=high_risk_count,
            moderate_risk_count=moderate_risk_count,
            total_predicted_overspend=total_predicted_overspend,
            category_forecasts=category_forecasts,
            year=year,
            month=month
        )


# Global service instance
forecast_service = ForecastService()
