from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    """Get financial summary for a specific month or all time."""
    try:
        summary = await dashboard_service.get_summary(year=year, month=month)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")


@router.get("/category-spending")
async def get_category_spending(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    """Get spending totals by category (expenses only)."""
    try:
        category_spending = await dashboard_service.get_category_spending(year=year, month=month)
        return category_spending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category spending: {str(e)}")


@router.get("/monthly-trend")
async def get_monthly_trend(months: int = Query(6, ge=1, le=12)):
    """Get monthly income and expenses for the past N months."""
    try:
        monthly_trend = await dashboard_service.get_monthly_trend(months=months)
        return monthly_trend
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monthly trend: {str(e)}")


@router.get("/daily-spending")
async def get_daily_spending(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    """Get daily expense totals for a specific month."""
    try:
        daily_spending = await dashboard_service.get_daily_spending(year=year, month=month)
        return daily_spending
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily spending: {str(e)}")


@router.get("/top-categories")
async def get_top_categories(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    limit: int = Query(5, ge=1, le=10)
):
    """Get top spending categories for a specific month."""
    try:
        top_categories = await dashboard_service.get_top_categories(year=year, month=month, limit=limit)
        return top_categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top categories: {str(e)}")


@router.get("/month-comparison")
async def get_month_comparison(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12)
):
    """Compare current month expenses with previous month."""
    try:
        comparison = await dashboard_service.get_month_comparison(year=year, month=month)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get month comparison: {str(e)}")
