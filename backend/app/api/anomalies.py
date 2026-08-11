from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from app.services.anomaly_service import anomaly_service
from app.schemas.anomaly import AnomalySummary, AnomalyItem
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("/summary", response_model=AnomalySummary)
async def get_anomaly_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get statistical anomaly detection summary and alert items for authenticated user."""
    try:
        summary = await anomaly_service.get_anomaly_summary(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate anomaly summary: {str(e)}")


@router.get("/", response_model=List[AnomalyItem])
async def get_anomalies(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    current_user: User = Depends(get_current_user)
):
    """Get list of flagged anomaly alerts for authenticated user."""
    try:
        summary = await anomaly_service.get_anomaly_summary(
            user_id=str(current_user.id),
            year=year,
            month=month
        )
        return summary.anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch anomalies: {str(e)}")
