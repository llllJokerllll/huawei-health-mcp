"""
Workout data routes.
"""

from datetime import date, datetime
from typing import Optional, List
import uuid

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import WorkoutData, WorkoutResponse

router = APIRouter()


@router.get("/workouts", response_model=WorkoutResponse)
async def get_workout_history(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format."),
    type: Optional[str] = Query(None, description="Workout type filter (e.g., running, cycling, swimming)"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get workout and exercise history from Huawei Health.
    
    Supports 100+ workout types including running, cycling, swimming, golf, and more.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else None
    
    try:
        raw_data = await client.get_workouts(target_date, type, limit)
        
        # Transform raw data to our model format
        workout_data: List[WorkoutData] = []
        
        for workout in raw_data.get("workouts", []):
            start_time = datetime.fromisoformat(
                workout.get("startTime", datetime.now().isoformat()).replace("Z", "+00:00")
            )
            end_time = datetime.fromisoformat(
                workout.get("endTime", datetime.now().isoformat()).replace("Z", "+00:00")
            )
            
            workout_data.append(WorkoutData(
                id=workout.get("id", str(uuid.uuid4())),
                type=workout.get("type", "unknown"),
                start=start_time,
                end=end_time,
                duration_minutes=workout.get("duration", 0),
                calories=workout.get("calories", 0.0),
                heart_rate_avg=workout.get("heartRateAvg", 60),
                heart_rate_max=workout.get("heartRateMax", 120),
                distance_meters=workout.get("distance")
            ))
        
        return WorkoutResponse(
            data=workout_data,
            count=len(workout_data)
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
