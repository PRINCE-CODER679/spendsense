from datetime import datetime
from typing import Optional
from app.schemas.transaction import TransactionType, TransactionCategory, TransactionSource


class Transaction:
    def __init__(
        self,
        user_id: str,
        amount: float,
        transaction_type: TransactionType,
        description: str,
        category: TransactionCategory,
        date: datetime,
        merchant: Optional[str] = None,
        payment_method: Optional[str] = None,
        notes: Optional[str] = None,
        source: TransactionSource = TransactionSource.MANUAL,
        fingerprint: Optional[str] = None,
        category_confidence: Optional[float] = None,
        category_source: Optional[str] = None,
        category_reason: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.merchant = merchant
        self.category = category
        self.date = date
        self.payment_method = payment_method
        self.notes = notes
        self.source = source
        self.fingerprint = fingerprint
        self.category_confidence = category_confidence
        self.category_source = category_source
        self.category_reason = category_reason
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "description": self.description,
            "merchant": self.merchant,
            "category": self.category.value,
            "date": self.date,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "source": self.source.value,
            "fingerprint": self.fingerprint,
            "category_confidence": self.category_confidence,
            "category_source": self.category_source,
            "category_reason": self.category_reason,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=str(data.get("_id")),
            user_id=data.get("user_id"),
            amount=data.get("amount"),
            transaction_type=TransactionType(data.get("transaction_type")),
            description=data.get("description"),
            merchant=data.get("merchant"),
            category=TransactionCategory(data.get("category")),
            date=data.get("date"),
            payment_method=data.get("payment_method"),
            notes=data.get("notes"),
            source=TransactionSource(data.get("source", "manual")),
            fingerprint=data.get("fingerprint"),
            category_confidence=data.get("category_confidence"),
            category_source=data.get("category_source"),
            category_reason=data.get("category_reason"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
