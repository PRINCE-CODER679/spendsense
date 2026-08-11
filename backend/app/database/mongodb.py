import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    async def connect(self):
        try:
            client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                tls=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=10000
            )
            await client.admin.command('ping')
            self.client = client
        except Exception as e:
            print(f"Primary MongoDB connection failed: {e}. Retrying standard CA...")
            client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000
            )
            self.client = client

        self.database = self.client[settings.DATABASE_NAME]
        print(f"Connected to MongoDB database: {settings.DATABASE_NAME}")

    async def close(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

    def get_database(self):
        return self.database


mongodb = MongoDB()
