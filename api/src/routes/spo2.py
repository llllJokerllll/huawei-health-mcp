"""
SpO2 (blood oxygen) data routes.
"""

from datetime import date, datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import SpO2Data, SpO2Response

router = APIRouter()


@router.get("/spo2", response_model=SpO2Response)
async def get_spo2(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get blood oxygen saturation (SpO2) data from Huawei Health.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_spo2(target_date)
        
        # Transform raw data to our model format
        spo2_data: List[SpO2Data] = []
        
        # Process continuous SpO2 readings
        if "continuous" in raw_data and raw_data["continuous"]:
            for point in raw_data["continuous"].get("dataPoints", []):
                spo2_data.append(SpO2Data(
                    timestamp=datetime.fromisoformat(point.get("startTime", "").replace("Z", "+00:00")),
                    value=point.get("value", 0.0)
                ))
        
        # Process instantaneous SpO2 readings
        if "instantaneous" in raw_data and raw_data["instantaneous"]:
            for point in raw_data["instantaneous"].get("dataPoints", []):
                spo2_data.append(SpO2Data(
                    timestamp=datetime.fromisoformat(point.get("startTime", "").replace("Z", "+00:00")),
                    value=point.get("value", 0.0)
                ))
        
        return SpO2Response(
            data=spo2_data,
            date=date_str
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
