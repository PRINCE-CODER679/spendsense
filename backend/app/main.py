from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.mongodb import mongodb
from app.api.transactions import router as transactions_router
from app.api.upload import router as upload_router
from app.api.dashboard import router as dashboard_router
from app.api.insights import router as insights_router
from app.api.budget import router as budget_router
from app.api.forecast import router as forecast_router
from app.api.anomalies import router as anomalies_router
from app.api.assistant import router as assistant_router
from app.services.transaction_service import transaction_service


app = FastAPI(
    title="SpendSense AI API",
    description="Smart Personal Finance Tracker API",
    version="1.0.0"
)

cors_origins = [
    "https://spendsense-psi-two.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    settings.FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)




app.include_router(transactions_router)
app.include_router(upload_router)
app.include_router(dashboard_router)
app.include_router(insights_router)
app.include_router(budget_router)
app.include_router(forecast_router)
app.include_router(anomalies_router)
app.include_router(assistant_router)



@app.on_event("startup")
async def startup_db_client():
    try:
        await mongodb.connect()
        await transaction_service.create_indexes()
    except Exception as e:
        print(f"Warning: Could not connect to MongoDB: {e}")
        print("Application will run in degraded mode without database")


@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.close()


@app.get("/")
async def root():
    return {
        "message": "SpendSense AI API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    from motor.motor_asyncio import AsyncIOMotorClient
    try:
        # Use a short-timeout client just for the health ping
        probe_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=3000
        )
        await probe_client.admin.command('ping')
        probe_client.close()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
