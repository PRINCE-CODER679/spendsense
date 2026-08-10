from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    async def connect(self):
        try:
            import certifi
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )
        except Exception:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
        self.database = self.client[settings.DATABASE_NAME]
        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")

    async def close(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

    def get_database(self):
        return self.database


mongodb = MongoDB()

