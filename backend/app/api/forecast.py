from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List
from app.services.forecast_service import forecast_service
from app.schemas.forecast import CategoryForecast, ForecastSummary
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/forecasts", tags=["forecasts"])


@router.get("/summary", response_model=ForecastSummary)
async def get_forecast_summary(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get overall monthly spending forecast summary and risk matrix for authenticated user."""
    try:
        summary = await forecast_service.get_forecast_summary(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast summary: {str(e)}")


@router.get("/categories", response_model=List[CategoryForecast])
async def get_category_forecasts(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get category-level spending forecasts and budget prediction risks for authenticated user."""
    try:
        forecasts = await forecast_service.get_category_forecasts(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return forecasts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate category forecasts: {str(e)}")
