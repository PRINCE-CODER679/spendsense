import asyncio
import ssl
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
    # Test custom SSLContext
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    await test_connect("custom ssl context cert_none", ssl_context=ctx)

    # Test tlsInsecure
    await test_connect("tlsInsecure", tlsInsecure=True)

if __name__ == "__main__":
    asyncio.run(main())
