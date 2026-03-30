"""
NaviAid CRUD – Async database helpers.
"""
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text, or_
from sqlalchemy.orm import selectinload

from app.models import User, UserProfile, Opportunity, Application
from app.schemas import (
    ProfileCreate, ProfileUpdate, OpportunityCreate, OpportunityUpdate, ApplicationCreate
)
from app.auth_utils import hash_password


# ─────────────────────────── Users ───────────────────────────

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.profile))
    )
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, password: str, name: str, role: str = "user") -> User:
    user = User(email=email, hashed_password=hash_password(password), name=name, role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_google_user(db: AsyncSession, email: str, name: str, google_id: str) -> User:
    user = User(email=email, name=name, google_id=google_id, role="user")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ────────────────────────── Profile ──────────────────────────

async def get_profile(db: AsyncSession, user_id: str) -> Optional[UserProfile]:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def upsert_profile(db: AsyncSession, user_id: str, data: ProfileCreate, embedding: Optional[list[float]] = None) -> UserProfile:
    profile = await get_profile(db, user_id)
    update_data = data.model_dump(exclude_unset=True)
    if embedding is not None:
        update_data["embedding"] = embedding
    if profile:
        for key, value in update_data.items():
            setattr(profile, key, value)
        await db.commit()
        await db.refresh(profile)
    else:
        profile = UserProfile(user_id=user_id, **update_data)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


# ──────────────────────── Opportunities ──────────────────────

async def list_opportunities(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    category: Optional[str] = None,
    is_active: bool = True,
) -> tuple[int, list[Opportunity]]:
    q = select(Opportunity).where(Opportunity.is_active == is_active)
    if category:
        q = q.where(Opportunity.category == category)
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit).order_by(Opportunity.trust_score.desc()))).scalars().all()
    return total, list(items)


async def get_opportunity(db: AsyncSession, opp_id: str) -> Optional[Opportunity]:
    result = await db.execute(select(Opportunity).where(Opportunity.id == opp_id))
    return result.scalar_one_or_none()


async def create_opportunity(db: AsyncSession, data: OpportunityCreate, embedding: Optional[list[float]] = None) -> Opportunity:
    opp = Opportunity(**data.model_dump(), embedding=embedding)
    db.add(opp)
    await db.commit()
    await db.refresh(opp)
    return opp


async def update_opportunity(db: AsyncSession, opp_id: str, data: OpportunityUpdate) -> Optional[Opportunity]:
    opp = await get_opportunity(db, opp_id)
    if not opp:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(opp, key, value)
    await db.commit()
    await db.refresh(opp)
    return opp


async def delete_opportunity(db: AsyncSession, opp_id: str) -> bool:
    opp = await get_opportunity(db, opp_id)
    if not opp:
        return False
    await db.delete(opp)
    await db.commit()
    return True


async def full_text_search_opportunities(db: AsyncSession, query: str, limit: int = 20) -> list[Opportunity]:
    """BM25-style full-text search using PostgreSQL tsvector."""
    sql = text("""
        SELECT * FROM opportunities
        WHERE is_active = true
          AND (
            to_tsvector('english', title || ' ' || description) @@ plainto_tsquery('english', :q)
            OR title ILIKE :like_q
          )
        ORDER BY ts_rank(to_tsvector('english', title || ' ' || description), plainto_tsquery('english', :q)) DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, {"q": query, "like_q": f"%{query}%", "limit": limit})
    rows = result.mappings().all()
    return [Opportunity(**dict(row)) for row in rows]


async def vector_search_opportunities(db: AsyncSession, embedding: list[float], limit: int = 20) -> list[tuple[Opportunity, float]]:
    """Cosine similarity search using pgvector."""
    sql = text("""
        SELECT *, 1 - (embedding <=> CAST(:emb AS vector)) AS cosine_sim
        FROM opportunities
        WHERE is_active = true AND embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:emb AS vector)
        LIMIT :limit
    """)
    result = await db.execute(sql, {"emb": str(embedding), "limit": limit})
    rows = result.mappings().all()
    out = []
    for row in rows:
        d = dict(row)
        sim = d.pop("cosine_sim", 0.0)
        opp = Opportunity(**{k: v for k, v in d.items() if hasattr(Opportunity, k)})
        out.append((opp, float(sim)))
    return out


# ────────────────────────── Applications ─────────────────────

async def get_user_applications(db: AsyncSession, user_id: str) -> list[Application]:
    result = await db.execute(
        select(Application)
        .where(Application.user_id == user_id)
        .options(selectinload(Application.opportunity))
        .order_by(Application.created_at.desc())
    )
    return list(result.scalars().all())


async def upsert_application(db: AsyncSession, user_id: str, data: ApplicationCreate) -> Application:
    # Check if already exists
    existing = await db.execute(
        select(Application).where(
            Application.user_id == user_id,
            Application.opportunity_id == data.opportunity_id,
        )
    )
    app = existing.scalar_one_or_none()
    if app:
        app.status = data.status
        app.notes = data.notes
    else:
        app = Application(user_id=user_id, **data.model_dump())
        db.add(app)
    await db.commit()
    await db.refresh(app)
    return app
