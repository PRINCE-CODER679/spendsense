from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.services.dashboard_service import dashboard_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get financial summary for a specific month or all time for authenticated user."""
    try:
        summary = await dashboard_service.get_summary(user_id=str(current_user.id), year=year, month=month)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")


@router.get("/category-spending")
async def get_category_spending(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get spending totals by category (expenses only) for authenticated user."""
    try:
        category_spending = await dashboard_service.get_category_spending(user_id=str(current_user.id), year=year, month=month)
        return category_spending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category spending: {str(e)}")


@router.get("/monthly-trend")
async def get_monthly_trend(
    months: int = Query(6, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get monthly income and expenses for the past N months for authenticated user."""
    try:
        monthly_trend = await dashboard_service.get_monthly_trend(user_id=str(current_user.id), months=months)
        return monthly_trend
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monthly trend: {str(e)}")


@router.get("/daily-spending")
async def get_daily_spending(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get daily expense totals for a specific month for authenticated user."""
    try:
        daily_spending = await dashboard_service.get_daily_spending(user_id=str(current_user.id), year=year, month=month)
        return daily_spending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily spending: {str(e)}")


@router.get("/top-categories")
async def get_top_categories(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    limit: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """Get top spending categories for a specific month for authenticated user."""
    try:
        top_categories = await dashboard_service.get_top_categories(user_id=str(current_user.id), year=year, month=month, limit=limit)
        return top_categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top categories: {str(e)}")


@router.get("/month-comparison")
async def get_month_comparison(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Compare current month expenses with previous month for authenticated user."""
    try:
        comparison = await dashboard_service.get_month_comparison(year=year, month=month, user_id=str(current_user.id))
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get month comparison: {str(e)}")
