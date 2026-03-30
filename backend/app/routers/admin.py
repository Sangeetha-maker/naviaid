"""
NaviAid Admin Router – CRUD for Opportunities (admin-only) + external sync.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.schemas import OpportunityCreate, OpportunityUpdate, OpportunityOut, PaginatedOpportunities
from app.routers.auth import require_admin
from app.ml.embed import encode_text, build_opportunity_text
from app.services.external_sync import run_full_sync

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/sync")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a full external data sync (JSearch, Adzuna, MyScheme, RSS).
    Runs synchronously and returns a summary.
    """
    result = await run_full_sync(db)
    return result




@router.get("/opportunities", response_model=PaginatedOpportunities)
async def list_all_opportunities(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    category: str | None = None,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    total, items = await crud.list_opportunities(db, limit=limit, offset=offset, category=category, is_active=True)
    return PaginatedOpportunities(total=total, limit=limit, offset=offset, items=[OpportunityOut.model_validate(i) for i in items])


@router.get("/opportunities/{opp_id}", response_model=OpportunityOut)
async def get_opportunity(
    opp_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    opp = await crud.get_opportunity(db, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return OpportunityOut.model_validate(opp)


@router.post("/opportunities", response_model=OpportunityOut, status_code=201)
async def create_opportunity(
    data: OpportunityCreate,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    # Generate embedding
    opp_text = build_opportunity_text(data.model_dump())
    embedding = encode_text(opp_text)
    opp = await crud.create_opportunity(db, data, embedding=embedding)
    return OpportunityOut.model_validate(opp)


@router.put("/opportunities/{opp_id}", response_model=OpportunityOut)
async def update_opportunity(
    opp_id: str,
    data: OpportunityUpdate,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    opp = await crud.update_opportunity(db, opp_id, data)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return OpportunityOut.model_validate(opp)


@router.delete("/opportunities/{opp_id}", status_code=204)
async def delete_opportunity(
    opp_id: str,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud.delete_opportunity(db, opp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Opportunity not found")


@router.get("/stats")
async def admin_stats(
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Returns high-level admin statistics."""
    from sqlalchemy import select, func
    from app.models import Opportunity, User, Application

    opp_count = (await db.execute(select(func.count(Opportunity.id)))).scalar_one()
    user_count = (await db.execute(select(func.count(User.id)))).scalar_one()
    app_count = (await db.execute(select(func.count(Application.id)))).scalar_one()

    return {
        "total_opportunities": opp_count,
        "total_users": user_count,
        "total_applications": app_count,
    }
