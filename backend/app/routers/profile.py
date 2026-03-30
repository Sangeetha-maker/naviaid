"""
NaviAid Profile Router – CRUD for user profile + application history.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.database import get_db
from app import crud
from app.schemas import ProfileCreate, ProfileUpdate, ProfileOut, ApplicationCreate, ApplicationOut
from app.routers.auth import get_current_user
from app.ml.embed import build_profile_text, encode_text
from app.models import User, UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=ProfileOut)
@router.get("/me", response_model=ProfileOut)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await crud.get_profile(db, current_user.id)
    if not profile:
        # Auto-create blank profile on first access
        import uuid
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            onboarding_complete=False,
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return ProfileOut.model_validate(profile)


@router.put("/", response_model=ProfileOut)
@router.patch("/me", response_model=ProfileOut)
async def upsert_my_profile(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await crud.get_profile(db, current_user.id)
    if not profile:
        import uuid
        profile = UserProfile(id=str(uuid.uuid4()), user_id=current_user.id)
        db.add(profile)
    # Update allowed fields
    allowed = {"age", "gender", "district", "annual_income", "education_level",
               "occupation", "caste_category", "interests", "onboarding_complete", "draft_step"}
    for k, v in data.items():
        if k in allowed and hasattr(profile, k):
            setattr(profile, k, v)
    # Map frontend field names
    # Map frontend field names
    if "education" in data:
        profile.education_level = data["education"]
    if "interested_categories" in data:
        profile.interests = data["interested_categories"]
    if "is_onboarded" in data:
        profile.onboarding_complete = data["is_onboarded"]

    # Also update the User name
    if "name" in data and data["name"]:
        current_user.name = data["name"]
        db.add(current_user)

    await db.commit()
    await db.refresh(profile)
    return ProfileOut.model_validate(profile)


@router.post("/applications", response_model=ApplicationOut, status_code=201)
async def save_application(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    app = await crud.upsert_application(db, current_user.id, data)
    # Reload with opportunity
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models import Application
    result = await db.execute(
        select(Application).where(Application.id == app.id).options(selectinload(Application.opportunity))
    )
    full_app = result.scalar_one()
    return ApplicationOut.model_validate(full_app)


@router.get("/applications", response_model=list[ApplicationOut])
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    apps = await crud.get_user_applications(db, current_user.id)
    return [ApplicationOut.model_validate(a) for a in apps]

    
@router.delete("/applications/{opportunity_id}", status_code=204)
async def delete_my_application(
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import delete
    from app.models import Application
    await db.execute(
        delete(Application).where(
            Application.user_id == current_user.id,
            Application.opportunity_id == opportunity_id
        )
    )
    await db.commit()
