from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.services.forecast_service import forecast_service
from app.schemas.forecast import CategoryForecast, ForecastSummary

router = APIRouter(prefix="/api/forecasts", tags=["forecasts"])


@router.get("/summary", response_model=ForecastSummary)
async def get_forecast_summary(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12)
):
    """Get overall monthly spending forecast summary and risk matrix."""
    try:
        summary = await forecast_service.get_forecast_summary(
            user_id="default_user",
            year=year,
            month=month
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast summary: {str(e)}")


@router.get("/categories", response_model=List[CategoryForecast])
async def get_category_forecasts(
    year: int = Query(None),
    month: int = Query(None, ge=1, le=12)
):
    """Get category-level spending forecasts and budget prediction risks."""
    try:
        forecasts = await forecast_service.get_category_forecasts(
            user_id="default_user",
            year=year,
            month=month
        )
        return forecasts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate category forecasts: {str(e)}")
