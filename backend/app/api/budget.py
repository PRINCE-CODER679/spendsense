from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse
from app.services.budget_service import budget_service

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.post("", response_model=BudgetResponse, status_code=201)
async def create_budget(budget: BudgetCreate):
    """Create a new budget."""
    try:
        created_budget = await budget_service.create_budget(budget)
        return BudgetResponse(**created_budget)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create budget: {str(e)}")


@router.get("", response_model=BudgetListResponse)
async def get_budgets(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    category: Optional[str] = Query(None)
):
    """Get all budgets with optional filters."""
    try:
        budgets = await budget_service.get_budgets(
            year=year,
            month=month,
            category=category
        )
        return BudgetListResponse(
            budgets=[BudgetResponse(**b) for b in budgets],
            total=len(budgets)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budgets: {str(e)}")


@router.get("/analysis/current")
async def get_budget_analysis(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12)
):
    """Get budget vs actual spending analysis."""
    try:
        analysis = await budget_service.get_budget_analysis(year=year, month=month)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budget analysis: {str(e)}")


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: str):
    """Get a specific budget by ID."""
    try:
        budget = await budget_service.get_budget(budget_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return BudgetResponse(**budget)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get budget: {str(e)}")


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: str, budget_data: BudgetUpdate):
    """Update a budget."""
    try:
        updated_budget = await budget_service.update_budget(budget_id, budget_data)
        if not updated_budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return BudgetResponse(**updated_budget)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update budget: {str(e)}")


@router.delete("/{budget_id}")
async def delete_budget(budget_id: str):
    """Delete a budget."""
    try:
        deleted = await budget_service.delete_budget(budget_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Budget not found")
        return {"message": "Budget deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete budget: {str(e)}")
