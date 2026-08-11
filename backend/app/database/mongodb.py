import os
import sys
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    async def connect(self):
        """
        Connect to MongoDB Atlas.
        Production (Render/Linux): Strictly enforces standard TLS certificate validation via certifi.where().
        Local Dev (Windows): Fallback to tlsAllowInvalidCertificates=True if local Windows OpenSSL CA store fails.
        """
        # Detect production environment (Render platform or Linux production)
        is_production = os.getenv("RENDER") is not None or os.getenv("ENVIRONMENT") == "production" or sys.platform != "win32"

        if is_production:
            # Production: Pure certifi Root CA validation. NO fallback to tlsAllowInvalidCertificates.
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000
            )
            self.database = self.client[settings.DATABASE_NAME]
            await self.database.command('ping')
            print(f"Connected to MongoDB database (Production TLS Enforced): {settings.DATABASE_NAME}")
            return

        # Local Windows Development
        try:
            client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )
            db = client[settings.DATABASE_NAME]
            await db.command('ping')
            self.client = client
            self.database = db
            print(f"Connected to MongoDB database (Local TLS Verified): {settings.DATABASE_NAME}")
        except Exception as e:
            print(f"Standard TLS CA validation failed on local dev ({e}). Using local dev TLS fallback...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=5000
            )
            self.database = self.client[settings.DATABASE_NAME]
            await self.database.command('ping')
            print(f"Connected to MongoDB database (Local Dev Fallback): {settings.DATABASE_NAME}")

    async def close(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

    def get_database(self):
        return self.database


mongodb = MongoDB()
