"""
Pydantic models for Huawei Health data.
Matches the MCP types defined in mcp-server/src/types.ts
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# --- Heart Rate ---

class HeartRateData(BaseModel):
    """Heart rate data point."""
    timestamp: datetime
    value: int = Field(..., ge=30, le=220, description="Heart rate in BPM")
    type: Literal["instantaneous", "continuous", "resting", "exercise"]


class HeartRateResponse(BaseModel):
    """Response for heart rate queries."""
    data: List[HeartRateData]
    date: str
    type: str


# --- Sleep ---

SleepPhase = Literal["deep", "light", "REM", "awake"]


class SleepSegment(BaseModel):
    """Sleep segment with phase information."""
    phase: SleepPhase
    start: datetime
    end: datetime
    duration_minutes: int = Field(..., ge=0)


class SleepData(BaseModel):
    """Complete sleep data for a night."""
    date: str
    bedtime: datetime
    wakeup: datetime
    duration_minutes: int = Field(..., ge=0)
    score: int = Field(..., ge=0, le=100, description="Sleep quality score 0-100")
    phases: List[SleepSegment]
    apnea_events: int = Field(..., ge=0)
    spo2_avg: float = Field(..., ge=0, le=100)


# --- SpO2 ---

class SpO2Data(BaseModel):
    """Blood oxygen saturation data point."""
    timestamp: datetime
    value: float = Field(..., ge=0, le=100, description="SpO2 percentage")


class SpO2Response(BaseModel):
    """Response for SpO2 queries."""
    data: List[SpO2Data]
    date: str


# --- Steps ---

class StepsData(BaseModel):
    """Daily steps data."""
    date: str
    steps: int = Field(..., ge=0)
    distance_meters: float = Field(..., ge=0)
    calories: float = Field(..., ge=0)


# --- Stress ---

StressDescription = Literal["relaxed", "normal", "moderate", "high", "very_high"]


class StressData(BaseModel):
    """Stress level data point."""
    timestamp: datetime
    level: int = Field(..., ge=1, le=100)
    description: StressDescription


class StressResponse(BaseModel):
    """Response for stress queries."""
    data: List[StressData]
    date: str


# --- Temperature ---

class TemperatureData(BaseModel):
    """Skin temperature data point."""
    timestamp: datetime
    value_celsius: float


class TemperatureResponse(BaseModel):
    """Response for temperature queries."""
    data: List[TemperatureData]
    date: str


# --- ECG ---

ECGResult = Literal["normal", "sinus_rhythm_with_premature_beats", "atrial_fibrillation", "unknown"]


class ECGData(BaseModel):
    """ECG analysis result."""
    timestamp: datetime
    result: ECGResult
    heart_rate: int = Field(..., ge=30, le=220)


class ECGResponse(BaseModel):
    """Response for ECG queries."""
    data: List[ECGData]
    date: str


# --- Workouts ---

class WorkoutData(BaseModel):
    """Workout summary data."""
    id: str
    type: str
    start: datetime
    end: datetime
    duration_minutes: int = Field(..., ge=0)
    calories: float = Field(..., ge=0)
    heart_rate_avg: int = Field(..., ge=30, le=220)
    heart_rate_max: int = Field(..., ge=30, le=220)
    distance_meters: Optional[float] = None


class WorkoutResponse(BaseModel):
    """Response for workout queries."""
    data: List[WorkoutData]
    count: int


# --- Daily Health Summary ---

class DailyHealthSummary(BaseModel):
    """Comprehensive daily health summary."""
    date: str
    heart_rate_resting: int
    heart_rate_avg: int
    heart_rate_max: int
    steps: int
    calories_active: float
    calories_total: float
    sleep_hours: float
    sleep_score: int
    spo2_avg: float
    stress_avg: float
    temperature_avg: float
    workouts: int


# --- OAuth Models ---

class OAuthAuthorizeRequest(BaseModel):
    """Request to start OAuth flow."""
    state: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    """OAuth callback with authorization code."""
    code: str
    state: Optional[str] = None


class TokenResponse(BaseModel):
    """OAuth token response."""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


# --- API Response Models ---

class HealthCheckResponse(BaseModel):
    """Health check endpoint response."""
    status: str = "ok"
    version: str
    huawei_api_connected: bool = False


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
