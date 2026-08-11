from typing import Optional, Dict
from datetime import datetime
from bson import ObjectId
from app.database.mongodb import mongodb
from app.models.user import User
from app.schemas.user import UserRegister
from app.utils.security import hash_password, verify_password


class UserService:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = mongodb.get_database().users
        return self._collection

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email address."""
        user_doc = await self.collection.find_one({"email": email.lower().strip()})
        if user_doc:
            return User.from_dict(user_doc)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Fetch a user by user_id string."""
        if not ObjectId.is_valid(user_id):
            return None
        user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return User.from_dict(user_doc)
        return None

    async def create_user(self, user_data: UserRegister) -> User:
        """Register a new user in MongoDB."""
        email_clean = user_data.email.lower().strip()
        
        # Check if email already exists
        existing = await self.get_user_by_email(email_clean)
        if existing:
            raise ValueError("Email is already registered")

        hashed_pwd = hash_password(user_data.password)
        now = datetime.utcnow()

        user_dict = {
            "email": email_clean,
            "password_hash": hashed_pwd,
            "full_name": user_data.full_name.strip() if user_data.full_name else None,
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id

        return User.from_dict(user_dict)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Verify user login credentials."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def create_indexes(self):
        """Create indexes for users collection."""
        try:
            collection = self.collection
            await collection.create_index([("email", 1)], unique=True)
        except Exception as e:
            print(f"Warning: Could not create user collection index: {e}")


user_service = UserService()
