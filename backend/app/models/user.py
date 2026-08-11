from datetime import datetime
from typing import Optional


class User:
    def __init__(
        self,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self):
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=str(data.get("_id")),
            email=data.get("email"),
            password_hash=data.get("password_hash"),
            full_name=data.get("full_name"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
