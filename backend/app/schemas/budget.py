from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class BudgetStatus(str, Enum):
    """Budget status based on spending percentage."""
    SAFE = "safe"
    WARNING = "warning"
    NEAR_LIMIT = "near_limit"
    EXCEEDED = "exceeded"


class BudgetCreate(BaseModel):
    """Schema for creating a budget."""
    amount: float = Field(..., gt=0, description="Budget amount must be greater than 0")
    category: Optional[str] = Field(None, description="Category for category-specific budget. None for overall budget")
    year: int = Field(..., ge=2020, le=2100, description="Budget year")
    month: int = Field(..., ge=1, le=12, description="Budget month")


class BudgetUpdate(BaseModel):
    """Schema for updating a budget."""
    amount: float = Field(..., gt=0, description="Budget amount must be greater than 0")


class BudgetResponse(BaseModel):
    """Schema for budget response."""
    id: str
    user_id: str
    amount: float
    category: Optional[str]
    year: int
    month: int
    created_at: datetime
    updated_at: datetime


class BudgetAnalysis(BaseModel):
    """Schema for budget vs actual spending analysis."""
    budget_id: str
    category: Optional[str]
    budget_amount: float
    actual_spending: float
    remaining: float
    percentage_used: float
    is_over_budget: bool
    over_budget_amount: float
    status: BudgetStatus
    year: int
    month: int


class BudgetListResponse(BaseModel):
    """Schema for list of budgets."""
    budgets: list[BudgetResponse]
    total: int


class BudgetAnalysisResponse(BaseModel):
    """Schema for budget analysis response."""
    overall_budget: Optional[BudgetAnalysis]
    category_budgets: list[BudgetAnalysis]
    year: int
    month: int
