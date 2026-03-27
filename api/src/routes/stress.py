"""
Stress data routes.
"""

from datetime import date, datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import StressData, StressResponse

router = APIRouter()


def get_stress_description(level: int) -> str:
    """Convert stress level (1-100) to description."""
    if level <= 20:
        return "relaxed"
    elif level <= 40:
        return "normal"
    elif level <= 60:
        return "moderate"
    elif level <= 80:
        return "high"
    else:
        return "very_high"


@router.get("/stress", response_model=StressResponse)
async def get_stress(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get stress levels and trends from Huawei Health.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_stress(target_date)
        
        # Transform raw data to our model format
        stress_data: List[StressData] = []
        
        if "dataPoints" in raw_data:
            for point in raw_data.get("dataPoints", []):
                level = point.get("value", 50)
                stress_data.append(StressData(
                    timestamp=datetime.fromisoformat(point.get("startTime", "").replace("Z", "+00:00")),
                    level=level,
                    description=get_stress_description(level)
                ))
        
        return StressResponse(
            data=stress_data,
            date=date_str
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
