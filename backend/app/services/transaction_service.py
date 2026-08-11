from typing import Optional, List, Union
from datetime import datetime
from bson import ObjectId
from app.database.mongodb import mongodb
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = mongodb.get_database().transactions
        return self._collection

    async def create_transaction(
        self,
        transaction_data: TransactionCreate,
        user_id: str,
        fingerprint: Optional[str] = None
    ) -> Transaction:
        transaction_dict = transaction_data.dict()
        transaction_dict["user_id"] = user_id
        transaction_dict["created_at"] = datetime.utcnow()
        if fingerprint:
            transaction_dict["fingerprint"] = fingerprint
        
        result = await self.collection.insert_one(transaction_dict)
        transaction_dict["_id"] = result.inserted_id
        
        return Transaction.from_dict(transaction_dict)

    async def get_transaction(self, transaction_id: str, user_id: str) -> Optional[Transaction]:
        if not ObjectId.is_valid(transaction_id):
            return None
        
        transaction = await self.collection.find_one({"_id": ObjectId(transaction_id), "user_id": user_id})
        if transaction:
            return Transaction.from_dict(transaction)
        return None

    async def get_transactions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "date",
        sort_order: int = -1
    ) -> tuple[List[Transaction], int]:
        query = {"user_id": user_id}
        
        if search:
            query["$or"] = [
                {"description": {"$regex": search, "$options": "i"}},
                {"merchant": {"$regex": search, "$options": "i"}}
            ]
        
        if category:
            query["category"] = category
        
        if transaction_type:
            query["transaction_type"] = transaction_type
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["date"] = date_query
        
        total = await self.collection.count_documents(query)
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort(sort_by, sort_order)
        transactions = await cursor.to_list(length=limit)
        
        return [Transaction.from_dict(t) for t in transactions], total

    async def update_transaction(
        self,
        transaction_id: str,
        transaction_data: Union[TransactionUpdate, dict],
        user_id: str
    ) -> Optional[Transaction]:
        if not ObjectId.is_valid(transaction_id):
            return None
        
        # Handle both TransactionUpdate objects and dicts
        if hasattr(transaction_data, 'dict'):
            update_dict = {k: v for k, v in transaction_data.dict().items() if v is not None}
        else:
            update_dict = {k: v for k, v in transaction_data.items() if v is not None}
        
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(transaction_id), "user_id": user_id},
            {"$set": update_dict}
        )
        
        if result.matched_count > 0 or result.modified_count > 0:
            return await self.get_transaction(transaction_id, user_id)
        return None

    async def delete_transaction(self, transaction_id: str, user_id: str) -> bool:
        if not ObjectId.is_valid(transaction_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(transaction_id), "user_id": user_id})
        return result.deleted_count > 0

    async def create_indexes(self):
        try:
            collection = self.collection
            await collection.create_index([("user_id", 1)])
            await collection.create_index([("date", -1)])
            await collection.create_index([("category", 1)])
            await collection.create_index([("transaction_type", 1)])
            await collection.create_index([("description", "text"), ("merchant", "text")])
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")


transaction_service = TransactionService()
