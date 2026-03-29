from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.domain.models import Application  ,TestRun , Script
from app.schemas.request import ApplicationLookup , TestRoundLookup
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ApplicationLookup])
async def list_applications(db: AsyncSession = Depends(get_db)) -> List[ApplicationLookup]:
    """Populate the Application Dropdown"""
    result = await db.execute(select(Application))
    return result.scalars().all()

@router.get("/{app_id}/rounds", response_model=List[TestRoundLookup])
async def get_test_rounds_by_app(app_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetch all test rounds for an application by joining through the Scripts table.
    Shows multiple tries for every script linked to this app.
    """
    # We select the TestRun details AND the Script name
    query = (
        select(
            TestRun.id,
            TestRun.script_id,
            Script.name.label("script_name"),
            TestRun.start_time,
            TestRun.end_time,
            TestRun.status
        )
        .join(Script, TestRun.script_id == Script.id)
        .where(Script.application_id == app_id)
        .where(TestRun.status == "COMPLETED")
        .order_by(TestRun.start_time.desc())
    )

    result = await db.execute(query)
    
    rounds = result.mappings().all()

    if not rounds:
        raise HTTPException(
            status_code=404, 
            detail=f"No completed test runs found for Application ID {app_id}"
        )

    return rounds