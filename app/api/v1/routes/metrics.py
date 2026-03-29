from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any , Dict

from app.schemas.request import MetricsAnalysisRequest
from app.domain.services.dataRetrieving import AnalysisService
from app.db.session import get_db

router = APIRouter()

@router.post("/retrieval" , response_model=Dict[str,Any])
async def get_metrics_from_db( request: MetricsAnalysisRequest, db: AsyncSession = Depends(get_db))-> Dict[str, Any]:
    """ This is the main entry point for the UI to get 'Shifted' and 'Smoothed' 
    metrics for any test run. It handles the 10+ parallel VictoriaMetrics 
    calls in one go."""

    service = AnalysisService(db)
    try:
        result = await service.execute_analysis(request)

        if not result.get("data") or len(result["data"]) == 0:
            return{
                "status": "empty",
                "message": "Connected to VM, but no data found. Check container labels or time range.",
                "calibration": result.get("calibration",{})                
            }
        
        return {
            "status": "success",
            "test_run_id": request.test_round_id if request.selection_mode == "test_round" else "manual",
            "calibration" : result.get("calibration") ,
            "metrics" : result.get("data")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics engine error:{str(e)}")