"""
Health summary routes.
"""

from datetime import date, datetime
from typing import Optional
import statistics

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import DailyHealthSummary

router = APIRouter()


@router.get("/summary", response_model=DailyHealthSummary)
async def get_health_summary(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    period: str = Query("daily", description="Summary period: daily or weekly"),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get comprehensive daily or weekly health summary.
    
    Combines heart rate, sleep, steps, SpO2, stress, and temperature data.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_health_summary(target_date)
        
        # Extract and aggregate data
        heart_rate_resting = 60
        heart_rate_avg = 70
        heart_rate_max = 120
        steps = 0
        calories_active = 0.0
        calories_total = 0.0
        sleep_hours = 0.0
        sleep_score = 0
        spo2_avg = 98.0
        stress_avg = 30.0
        temperature_avg = 36.5
        workouts = 0
        
        # Process steps data
        if raw_data.get("steps") and "polymerizeData" in raw_data["steps"]:
            for point in raw_data["steps"].get("polymerizeData", []):
                steps = point.get("value", 0)
                calories_active = point.get("calories", 0.0)
                break
        
        # Process heart rate data
        hr_values = []
        if raw_data.get("heart_rate"):
            for hr_type in ["instantaneous", "continuous"]:
                if hr_type in raw_data["heart_rate"] and raw_data["heart_rate"][hr_type]:
                    for point in raw_data["heart_rate"][hr_type].get("dataPoints", []):
                        hr_values.append(point.get("value", 0))
        
        if hr_values:
            heart_rate_avg = int(statistics.mean(hr_values))
            heart_rate_max = max(hr_values)
        
        # Process sleep data
        if raw_data.get("sleep") and "sleepData" in raw_data["sleep"]:
            sleep_info = raw_data["sleep"]["sleepData"]
            sleep_hours = sleep_info.get("duration", 0) / 60
            sleep_score = sleep_info.get("score", 0)
        
        # Process SpO2 data
        spo2_values = []
        if raw_data.get("spo2"):
            for spo2_type in ["continuous", "instantaneous"]:
                if spo2_type in raw_data["spo2"] and raw_data["spo2"][spo2_type]:
                    for point in raw_data["spo2"][spo2_type].get("dataPoints", []):
                        spo2_values.append(point.get("value", 0.0))
        
        if spo2_values:
            spo2_avg = statistics.mean(spo2_values)
        
        # Process stress data
        stress_values = []
        if raw_data.get("stress") and "dataPoints" in raw_data["stress"]:
            for point in raw_data["stress"].get("dataPoints", []):
                stress_values.append(point.get("value", 0))
        
        if stress_values:
            stress_avg = statistics.mean(stress_values)
        
        # Process temperature data
        temp_values = []
        if raw_data.get("temperature") and "dataPoints" in raw_data["temperature"]:
            for point in raw_data["temperature"].get("dataPoints", []):
                temp_values.append(point.get("value", 36.5))
        
        if temp_values:
            temperature_avg = statistics.mean(temp_values)
        
        # Count workouts
        if raw_data.get("workouts"):
            workouts = len(raw_data.get("workouts", {}).get("workouts", []))
        
        return DailyHealthSummary(
            date=date_str,
            heart_rate_resting=heart_rate_resting,
            heart_rate_avg=heart_rate_avg,
            heart_rate_max=heart_rate_max,
            steps=steps,
            calories_active=calories_active,
            calories_total=calories_total,
            sleep_hours=sleep_hours,
            sleep_score=sleep_score,
            spo2_avg=spo2_avg,
            stress_avg=stress_avg,
            temperature_avg=temperature_avg,
            workouts=workouts
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
