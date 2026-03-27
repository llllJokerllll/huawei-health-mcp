"""
FastAPI main application for Huawei Health MCP Backend API.
"""

from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .storage import get_storage, close_storage, Storage
from .auth import OAuthManager, OAuthError
from .huawei_client import HuaweiClient, HuaweiAPIError
from .models import (
    HealthCheckResponse,
    ErrorResponse,
    HeartRateData, HeartRateResponse,
    SleepData,
    SpO2Data, SpO2Response,
    StepsData,
    StressData, StressResponse,
    TemperatureData, TemperatureResponse,
    ECGData, ECGResponse,
    WorkoutData, WorkoutResponse,
    DailyHealthSummary,
    TokenResponse, OAuthCallbackRequest, RefreshTokenRequest,
)

settings = get_settings()

# Global instances
storage: Optional[Storage] = None
oauth_manager: Optional[OAuthManager] = None
huawei_client: Optional[HuaweiClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global storage, oauth_manager, huawei_client
    
    # Startup
    storage = await get_storage()
    oauth_manager = OAuthManager(storage)
    huawei_client = HuaweiClient(oauth_manager, storage)
    
    yield
    
    # Shutdown
    if huawei_client:
        await huawei_client.close()
    await close_storage()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for Huawei Health MCP Server",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dependencies ---

def get_oauth_manager() -> OAuthManager:
    if oauth_manager is None:
        raise HTTPException(status_code=500, detail="OAuth manager not initialized")
    return oauth_manager


def get_huawei_client() -> HuaweiClient:
    if huawei_client is None:
        raise HTTPException(status_code=500, detail="Huawei client not initialized")
    return huawei_client


# --- Health Check ---

@app.get("/api/v1/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    client = get_huawei_client()
    is_authenticated = await oauth_manager.is_authenticated() if oauth_manager else False
    
    return HealthCheckResponse(
        status="ok",
        version=settings.app_version,
        huawei_api_connected=is_authenticated
    )


# --- Import and include route modules ---

from .routes import auth, heart_rate, sleep, spo2, steps, stress, temperature, ecg, workouts, summary

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(heart_rate.router, prefix="/api/v1", tags=["Heart Rate"])
app.include_router(sleep.router, prefix="/api/v1", tags=["Sleep"])
app.include_router(spo2.router, prefix="/api/v1", tags=["SpO2"])
app.include_router(steps.router, prefix="/api/v1", tags=["Steps"])
app.include_router(stress.router, prefix="/api/v1", tags=["Stress"])
app.include_router(temperature.router, prefix="/api/v1", tags=["Temperature"])
app.include_router(ecg.router, prefix="/api/v1", tags=["ECG"])
app.include_router(workouts.router, prefix="/api/v1", tags=["Workouts"])
app.include_router(summary.router, prefix="/api/v1", tags=["Summary"])


# --- Error handlers ---

@app.exception_handler(OAuthError)
async def oauth_error_handler(request, exc: OAuthError):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=401,
        content={"error": str(exc), "code": exc.code}
    )


@app.exception_handler(HuaweiAPIError)
async def huawei_api_error_handler(request, exc: HuaweiAPIError):
    from fastapi.responses import JSONResponse
    status_code = exc.status_code or 500
    return JSONResponse(
        status_code=status_code,
        content={"error": str(exc), "code": exc.error_code}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
