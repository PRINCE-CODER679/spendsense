import asyncio
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = "mongodb+srv://asrarmulla99_db_user:y7iHAgEvO6lG4Ttw@cluster0.jodunvl.mongodb.net/?appName=Cluster0"

async def test_connect(name, **kwargs):
    print(f"Testing {name}...")
    try:
        client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000, **kwargs)
        db = client["spendsense_ai"]
        collections = await db.list_collection_names()
        print(f"SUCCESS {name}! Collections:", collections)
        client.close()
        return True
    except Exception as e:
        print(f"FAILED {name}: {e}")
        return False

async def main():
    await test_connect("certifi", tlsCAFile=certifi.where())
    await test_connect("no extra ca")
    await test_connect("tlsAllowInvalidCertificates", tlsAllowInvalidCertificates=True)

if __name__ == "__main__":
    asyncio.run(main())
