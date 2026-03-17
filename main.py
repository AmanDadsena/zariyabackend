from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # IMPORT THIS
import models
from database import engine
from routers import store, dashboard, auth

app = FastAPI(title="Localink Engine API")

# --- ADD THIS CORS BLOCK ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development. In production, put your actual website URLs here.
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, PUT, DELETE
    allow_headers=["*"],
)
# ---------------------------

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app.include_router(auth.router, tags=["Authentication"])
app.include_router(store.router, tags=["Storefront"])
app.include_router(dashboard.router, tags=["Vendor Dashboard"])

@app.get("/health")
async def health_check():
    return {"status": "Engine Room is Online, Async, Locked, and Web-Ready"}