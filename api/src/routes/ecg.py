"""
ECG data routes.
"""

from datetime import date, datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Query

from ..huawei_client import HuaweiClient, HuaweiAPIError
from ..main import get_huawei_client
from ..models import ECGData, ECGResponse

router = APIRouter()


def map_ecg_result(result_code: int) -> str:
    """Map ECG result code to description."""
    result_map = {
        1: "normal",
        2: "sinus_rhythm_with_premature_beats",
        3: "atrial_fibrillation",
    }
    return result_map.get(result_code, "unknown")


@router.get("/ecg", response_model=ECGResponse)
async def get_ecg(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format. Defaults to today."),
    client: HuaweiClient = Depends(get_huawei_client)
):
    """
    Get ECG analysis results from Huawei Health.
    
    Results can be normal, sinus rhythm with premature beats, or atrial fibrillation.
    """
    # Parse date
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
    date_str = target_date.strftime("%Y-%m-%d")
    
    try:
        raw_data = await client.get_ecg(target_date)
        
        # Transform raw data to our model format
        ecg_data: List[ECGData] = []
        
        if "dataPoints" in raw_data:
            for point in raw_data.get("dataPoints", []):
                ecg_data.append(ECGData(
                    timestamp=datetime.fromisoformat(point.get("startTime", "").replace("Z", "+00:00")),
                    result=map_ecg_result(point.get("result", 0)),
                    heart_rate=point.get("heartRate", 60)
                ))
        
        return ECGResponse(
            data=ecg_data,
            date=date_str
        )
        
    except HuaweiAPIError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": str(e), "code": e.error_code}
        )
