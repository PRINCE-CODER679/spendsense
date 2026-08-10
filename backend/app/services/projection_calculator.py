from datetime import datetime, timedelta
from typing import Dict, Optional
from calendar import monthrange


class ProjectionCalculator:
    """Calculate spending projections based on current spending rate."""
    
    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """Get the number of days in a specific month."""
        return monthrange(year, month)[1]
    
    @staticmethod
    def get_current_day_of_month() -> int:
        """Get the current day of the month."""
        return datetime.now().day
    
    @staticmethod
    def calculate_monthly_projection(current_spending: float, days_elapsed: int, days_in_month: int) -> float:
        """
        Calculate projected monthly spending based on current rate.
        
        Formula: (current_spending / days_elapsed) * days_in_month
        """
        if days_elapsed == 0 or days_in_month == 0:
            return 0.0
        
        daily_rate = current_spending / days_elapsed
        projected = daily_rate * days_in_month
        
        return round(projected, 2)
    
    @staticmethod
    def calculate_category_projection(
        current_spending: float,
        year: int,
        month: int,
        current_day: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate category spending projection for the current month.
        
        Returns:
            {
                "current_spending": float,
                "days_elapsed": int,
                "days_in_month": int,
                "daily_rate": float,
                "projected_spending": float
            }
        """
        if current_day is None:
            current_day = datetime.now().day
        
        days_in_month = ProjectionCalculator.get_days_in_month(year, month)
        days_elapsed = min(current_day, days_in_month)
        
        if days_elapsed == 0:
            daily_rate = 0.0
        else:
            daily_rate = current_spending / days_elapsed
        
        projected_spending = ProjectionCalculator.calculate_monthly_projection(
            current_spending, days_elapsed, days_in_month
        )
        
        return {
            "current_spending": current_spending,
            "days_elapsed": days_elapsed,
            "days_in_month": days_in_month,
            "daily_rate": round(daily_rate, 2),
            "projected_spending": projected_spending
        }
    
    @staticmethod
    def calculate_difference_from_average(
        current_or_projected: float,
        historical_average: float
    ) -> Dict[str, float]:
        """
        Calculate the difference and percentage difference from historical average.
        
        Returns:
            {
                "difference": float,
                "percentage_difference": float,
                "is_above_average": bool
            }
        """
        if historical_average == 0:
            return {
                "difference": current_or_projected,
                "percentage_difference": 0.0,
                "is_above_average": current_or_projected > 0
            }
        
        difference = current_or_projected - historical_average
        percentage_difference = (difference / historical_average) * 100
        
        return {
            "difference": round(difference, 2),
            "percentage_difference": round(percentage_difference, 2),
            "is_above_average": difference > 0
        }
