"""
Heart rate data routes.
"""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import HeartRateData, HeartRateResponse

router = APIRouter()


@router.get("/heart-rate", response_model=HeartRateResponse)
async def get_heart_rate(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    type: str = Query("all", description="Type of heart rate data: instantaneous, continuous, resting, exercise, all"),
    start_time: Optional[str] = Query(None, description="Start time in HH:MM format"),
    end_time: Optional[str] = Query(None, description="End time in HH:MM format"),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get heart rate data from Huawei Health.
    
    Returns instantaneous, continuous, resting, and exercise heart rate data.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_heart_rate(target_date, type)
        
        # Transform raw data to our model format
        heart_rate_data: List[HeartRateData] = []
        
        # Process instantaneous heart rate
        if "instantaneous" in raw_data and raw_data["instantaneous"]:
            for point in raw_data["instantaneous"].get("dataPoints", []):
                heart_rate_data.append(HeartRateData(
                    timestamp=datetime.fromisoformat(point.get("startTime", "").replace("Z", "+00:00")),
                    value=point.get("value", 0),
                    type="instantaneous"
                ))
        
        # Process continuous heart rate
        if "continuous" in raw_data and raw_data["continuous"]:
            for point in raw_data["continuous"].get("dataPoints", []):
                heart_rate_data.append(HeartRateData(
                    timestamp=datetime.fromisoformat(point.get("startTime", "").replace("Z", "+00:00")),
                    value=point.get("value", 0),
                    type="continuous"
                ))
        
        return HeartRateResponse(
            data=heart_rate_data,
            date=date_str,
            type=type
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
