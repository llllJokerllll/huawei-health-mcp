"""
Steps data routes.
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import StepsData

router = APIRouter()


@router.get("/steps", response_model=StepsData)
async def get_steps(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get daily step count, distance, and calories from Huawei Health.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_steps(target_date)
        
        # Transform raw data to our model format
        steps = 0
        distance_meters = 0.0
        calories = 0.0
        
        if "polymerizeData" in raw_data:
            for data_point in raw_data.get("polymerizeData", []):
                if data_point.get("dataTypeName") == "com.huawei.continuous.steps.delta":
                    steps = data_point.get("value", 0)
                    distance_meters = data_point.get("distance", 0.0)
                    calories = data_point.get("calories", 0.0)
                    break
        
        return StepsData(
            date=date_str,
            steps=steps,
            distance_meters=distance_meters,
            calories=calories
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
