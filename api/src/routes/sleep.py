"""
Sleep data routes.
"""

from datetime import date, datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import SleepData, SleepSegment

router = APIRouter()


@router.get("/sleep", response_model=SleepData)
async def get_sleep_data(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to last night."),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get sleep analysis from Huawei Health.
    
    Includes sleep phases (deep, light, REM), duration, quality score, and apnea events.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_sleep(target_date)
        
        # Transform raw data to our model format
        # This is a simplified transformation - actual implementation depends on Huawei API response structure
        phases: List[SleepSegment] = []
        
        # Extract sleep phases from raw data
        if "sleepData" in raw_data:
            for segment in raw_data.get("sleepData", {}).get("sleepSegments", []):
                phase_map = {
                    1: "deep",
                    2: "light", 
                    3: "REM",
                    4: "awake"
                }
                phases.append(SleepSegment(
                    phase=phase_map.get(segment.get("phase", 2), "light"),
                    start=datetime.fromisoformat(segment.get("startTime", "").replace("Z", "+00:00")),
                    end=datetime.fromisoformat(segment.get("endTime", "").replace("Z", "+00:00")),
                    duration_minutes=segment.get("duration", 0)
                ))
        
        # Calculate sleep metrics
        bedtime = datetime.now()
        wakeup = datetime.now()
        duration = 0
        score = 0
        apnea_events = 0
        spo2_avg = 0.0
        
        if "sleepData" in raw_data:
            sleep_info = raw_data["sleepData"]
            bedtime = datetime.fromisoformat(sleep_info.get("bedtime", datetime.now().isoformat()).replace("Z", "+00:00"))
            wakeup = datetime.fromisoformat(sleep_info.get("wakeup", datetime.now().isoformat()).replace("Z", "+00:00"))
            duration = sleep_info.get("duration", 0)
            score = sleep_info.get("score", 0)
            apnea_events = sleep_info.get("apneaEvents", 0)
            spo2_avg = sleep_info.get("spo2Avg", 0.0)
        
        return SleepData(
            date=date_str,
            bedtime=bedtime,
            wakeup=wakeup,
            duration_minutes=duration,
            score=score,
            phases=phases,
            apnea_events=apnea_events,
            spo2_avg=spo2_avg
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
