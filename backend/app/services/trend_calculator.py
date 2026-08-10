from typing import Dict, List, Optional
from enum import Enum


class TrendDirection(Enum):
    """Trend direction classification."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


class TrendCalculator:
    """Calculate spending trends based on historical data."""
    
    @staticmethod
    def calculate_trend(
        current_period_spending: float,
        previous_period_spending: float,
        threshold_percentage: float = 10.0
    ) -> Dict[str, any]:
        """
        Calculate trend direction and magnitude between two periods.
        
        Args:
            current_period_spending: Spending in current period
            previous_period_spending: Spending in previous period
            threshold_percentage: Threshold to classify as stable (default 10%)
        
        Returns:
            {
                "direction": str (increasing/decreasing/stable),
                "percentage_change": float,
                "absolute_change": float,
                "is_significant": bool
            }
        """
        if previous_period_spending == 0:
            # If previous period had no spending, classify based on current
            if current_period_spending == 0:
                direction = TrendDirection.STABLE.value
            else:
                direction = TrendDirection.INCREASING.value
            percentage_change = 0.0
        else:
            percentage_change = ((current_period_spending - previous_period_spending) / previous_period_spending) * 100
            absolute_change = abs(percentage_change)
            
            if absolute_change <= threshold_percentage:
                direction = TrendDirection.STABLE.value
            elif percentage_change > 0:
                direction = TrendDirection.INCREASING.value
            else:
                direction = TrendDirection.DECREASING.value
        
        absolute_change = current_period_spending - previous_period_spending
        is_significant = abs(percentage_change) > threshold_percentage
        
        return {
            "direction": direction,
            "percentage_change": round(percentage_change, 2),
            "absolute_change": round(absolute_change, 2),
            "is_significant": is_significant
        }
    
    @staticmethod
    def calculate_historical_average(spending_values: List[float]) -> float:
        """
        Calculate the average spending from a list of values.
        
        Returns 0.0 if the list is empty.
        """
        if not spending_values:
            return 0.0
        
        return round(sum(spending_values) / len(spending_values), 2)
    
    @staticmethod
    def calculate_moving_average(spending_values: List[float], window_size: int = 3) -> List[float]:
        """
        Calculate moving average for spending values.
        
        Args:
            spending_values: List of spending values
            window_size: Size of the moving average window
        
        Returns:
            List of moving averages (same length as input, with None for early values)
        """
        if not spending_values:
            return []
        
        moving_averages = []
        for i in range(len(spending_values)):
            if i < window_size - 1:
                moving_averages.append(None)
            else:
                window = spending_values[i - window_size + 1:i + 1]
                avg = sum(window) / window_size
                moving_averages.append(round(avg, 2))
        
        return moving_averages
    
    @staticmethod
    def compare_with_multiple_periods(
        current_spending: float,
        historical_spending: List[float],
        threshold_percentage: float = 10.0
    ) -> Dict[str, any]:
        """
        Compare current spending with multiple historical periods.
        
        Returns:
            {
                "current": float,
                "historical_average": float,
                "historical_min": float,
                "historical_max": float,
                "trend": dict (from calculate_trend),
                "is_above_average": bool,
                "is_above_max": bool,
                "is_below_min": bool
            }
        """
        if not historical_spending:
            return {
                "current": current_spending,
                "historical_average": 0.0,
                "historical_min": 0.0,
                "historical_max": 0.0,
                "trend": {
                    "direction": TrendDirection.STABLE.value,
                    "percentage_change": 0.0,
                    "absolute_change": 0.0,
                    "is_significant": False
                },
                "is_above_average": current_spending > 0,
                "is_above_max": False,
                "is_below_min": False
            }
        
        historical_average = TrendCalculator.calculate_historical_average(historical_spending)
        historical_min = min(historical_spending)
        historical_max = max(historical_spending)
        
        # Use the most recent historical period for trend calculation
        most_recent_historical = historical_spending[-1]
        trend = TrendCalculator.calculate_trend(current_spending, most_recent_historical, threshold_percentage)
        
        return {
            "current": current_spending,
            "historical_average": historical_average,
            "historical_min": historical_min,
            "historical_max": historical_max,
            "trend": trend,
            "is_above_average": current_spending > historical_average,
            "is_above_max": current_spending > historical_max,
            "is_below_min": current_spending < historical_min
        }
