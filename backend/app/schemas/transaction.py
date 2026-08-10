from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCategory(str, Enum):
    FOOD = "Food"
    GROCERIES = "Groceries"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    BILLS = "Bills"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    RENT = "Rent"
    TRAVEL = "Travel"
    SALARY = "Salary"
    INVESTMENT = "Investment"
    OTHER = "Other"


class TransactionSource(str, Enum):
    MANUAL = "manual"
    IMPORTED = "imported"
    RULE = "rule"


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount must be greater than 0")
    transaction_type: TransactionType
    description: str = Field(..., min_length=1, description="Description cannot be empty")
    merchant: Optional[str] = None
    category: TransactionCategory
    date: datetime
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    source: TransactionSource = TransactionSource.MANUAL
    fingerprint: Optional[str] = None
    category_confidence: Optional[float] = None
    category_source: Optional[str] = None
    category_reason: Optional[str] = None


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[TransactionType] = None
    description: Optional[str] = Field(None, min_length=1)
    merchant: Optional[str] = None
    category: Optional[TransactionCategory] = None
    date: Optional[datetime] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    category_source: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    source: TransactionSource
    fingerprint: Optional[str] = None
    category_confidence: Optional[float] = None
    category_source: Optional[str] = None
    category_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    per_page: int
