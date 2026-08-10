from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.transaction import TransactionType, TransactionCategory, TransactionSource


class TransactionPreview(BaseModel):
    date: datetime
    amount: float
    transaction_type: TransactionType
    description: str
    merchant: str
    category: TransactionCategory
    payment_method: str
    notes: str
    source: TransactionSource
    fingerprint: str
    category_confidence: Optional[float] = None
    category_source: Optional[str] = None
    category_reason: Optional[str] = None
    is_duplicate: bool = False
    error: Optional[str] = None


class StatementPreviewResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    transactions: List[TransactionPreview]
    errors: List[str] = []


class ConfirmImportRequest(BaseModel):
    transactions: List[TransactionPreview]


class ConfirmImportResponse(BaseModel):
    success: bool
    imported: int
    skipped: int
    errors: List[str] = []
