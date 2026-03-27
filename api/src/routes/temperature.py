"""
Temperature data routes.
"""

from datetime import date, datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import TemperatureData, TemperatureResponse

router = APIRouter()


@router.get("/temperature", response_model=TemperatureResponse)
async def get_temperature(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get skin temperature readings from Huawei Health Watch GT 5 Pro.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_temperature(target_date)
        
        # Transform raw data to our model format
        temperature_data: List[TemperatureData] = []
        
        if "dataPoints" in raw_data:
            for point in raw_data.get("dataPoints", []):
                temperature_data.append(TemperatureData(
                    timestamp=datetime.fromisoformat(point.get("startTime", "").replace("Z", "+00:00")),
                    value_celsius=point.get("value", 36.5)
                ))
        
        return TemperatureResponse(
            data=temperature_data,
            date=date_str
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
