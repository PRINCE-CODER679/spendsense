from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class AnomalyType(str, Enum):
    UNUSUAL_AMOUNT = "unusual_amount"
    NEW_CATEGORY = "new_category"
    DAILY_SPIKE = "daily_spike"


class AnomalySeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AnomalyItem(BaseModel):
    """Details of a single flagged anomaly."""
    id: str = Field(..., description="Unique anomaly identifier")
    transaction_id: Optional[str] = Field(None, description="Associated transaction ID if applicable")
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Detailed explanation of the anomaly")
    category: str = Field(..., description="Spending category")
    amount: float = Field(..., description="Transaction or event amount")
    average_amount: float = Field(0.0, description="Historical category average amount")
    z_score: Optional[float] = Field(None, description="Statistical Z-Score if applicable")
    multiplier: Optional[float] = Field(None, description="Multiplier over average if applicable")
    date: str = Field(..., description="Date of occurrence (YYYY-MM-DD)")
    confidence_level: str = Field("high", description="Detection confidence: low, medium, high")


class AnomalySummary(BaseModel):
    """Summary of all anomalies detected for a period."""
    total_anomalies: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    unusual_amount_count: int
    new_category_count: int
    daily_spike_count: int
    anomalies: List[AnomalyItem]
    year: int
    month: int
