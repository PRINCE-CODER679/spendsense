from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.insights_service import insights_service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/")
async def get_insights(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get all spending insights and projections for authenticated user."""
    try:
        insights = await insights_service.generate_all_insights(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


@router.get("/category")
async def get_category_insights(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get category-specific insights for authenticated user."""
    try:
        category_insights = await insights_service.generate_category_insights(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return {
            "category_insights": category_insights,
            "year": year,
            "month": month
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate category insights: {str(e)}")


@router.get("/savings")
async def get_savings_insights(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get savings-related insights for authenticated user."""
    try:
        savings_insights = await insights_service.generate_savings_insights(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return {
            "savings_insights": savings_insights,
            "year": year,
            "month": month
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate savings insights: {str(e)}")


@router.get("/projection")
async def get_monthly_projection(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get monthly spending projection for authenticated user."""
    try:
        projection = await insights_service.generate_monthly_projection_insight(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return {
            "projection": projection,
            "year": year,
            "month": month
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate projection: {str(e)}")


@router.get("/forecast/summary")
async def get_insights_forecast_summary(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get overall monthly spending forecast summary and risk matrix for authenticated user."""
    from app.services.forecast_service import forecast_service
    try:
        summary = await forecast_service.get_forecast_summary(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast summary: {str(e)}")


@router.get("/forecast/categories")
async def get_insights_category_forecasts(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get category-level spending forecasts and budget prediction risks for authenticated user."""
    from app.services.forecast_service import forecast_service
    try:
        forecasts = await forecast_service.get_category_forecasts(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return forecasts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate category forecasts: {str(e)}")
