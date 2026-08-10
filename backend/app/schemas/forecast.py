from pydantic import BaseModel, Field
from typing import List, Optional


class CategoryForecast(BaseModel):
    """Forecast metrics for a single spending category."""
    category: str
    current_spending: float = Field(..., description="Amount spent so far in the current month")
    daily_rate: float = Field(..., description="Average daily spending rate")
    projected_spending: float = Field(..., description="Forecasted month-end spending total")
    historical_average: float = Field(..., description="6-month historical monthly average")
    budget_amount: Optional[float] = Field(None, description="Current monthly budget for this category, if any")
    projected_overspend: float = Field(0.0, description="Predicted overspend amount above budget or historical average")
    risk_level: str = Field("safe", description="Overspending risk level: safe, moderate_risk, high_risk")
    trend_direction: str = Field("stable", description="Trend direction: increasing, decreasing, stable")
    percentage_above_baseline: float = Field(0.0, description="Percentage above budget or historical average")
    confidence_level: str = Field("high", description="Projection confidence level: low, medium, high")
    days_remaining: int = Field(0, description="Days remaining in the month")


class ForecastSummary(BaseModel):
    """Summary of spending forecasts and budget predictions for a month."""
    overall_current_spending: float
    overall_projected_spending: float
    days_elapsed: int
    days_in_month: int
    days_remaining: int = Field(0, description="Days remaining in the month")
    confidence_level: str = Field("high", description="Projection confidence level: low, medium, high")
    daily_burn_rate: float
    high_risk_count: int
    moderate_risk_count: int
    total_predicted_overspend: float
    category_forecasts: List[CategoryForecast]
    year: int
    month: int
