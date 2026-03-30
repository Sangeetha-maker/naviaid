"""
NaviAid Recommendations Router – Rules + Vector hybrid ranking.
GET /reco/ → top-10 personalized opportunities.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.database import get_db
from app.models import UserProfile, Opportunity, User
from app.schemas import RecoResponse, RecoItem, OpportunityOut
from app.routers.auth import get_current_user
from app.ml.embed import build_profile_text, encode_text, cosine_similarity
from app.ml.ranker import evaluate_rules, geo_score, composite_score
from app import crud

router = APIRouter(prefix="/reco", tags=["recommendations"])


@router.get("/", response_model=RecoResponse)
async def get_recommendations(
    limit: int = 10,
    category: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return top-N personalized opportunity recommendations for the current user."""
    profile = await crud.get_profile(db, current_user.id)
    if not profile:
        import uuid
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            onboarding_complete=False,
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    profile_dict = {
        "age": profile.age,
        "gender": profile.gender,
        "district": profile.district,
        "annual_income": profile.annual_income,
        "caste_category": profile.caste_category,
        "education_level": profile.education_level,
        "skills": profile.skills or [],
        "interests": profile.interests or [],
        "is_differently_abled": profile.is_differently_abled,
    }

    # Get or create profile embedding
    if profile.embedding:
        profile_emb = json.loads(profile.embedding) if isinstance(profile.embedding, str) else profile.embedding
    else:
        profile_text = build_profile_text(profile_dict)
        profile_emb = encode_text(profile_text)
        # Save embedding back
        profile.embedding = json.dumps(profile_emb)
        await db.commit()

    # Fetch all active opportunities
    total_opps, opps = await crud.list_opportunities(db, limit=500, category=category)

    scored: list[tuple[float, RecoItem]] = []

    for opp in opps:
        opp_dict = {
            "locations": opp.locations or [],
            "is_pan_india": opp.is_pan_india,
            "eligibility": opp.eligibility or {},
        }

        # 1. Rules score
        rules_sc, checks, reasons = evaluate_rules(profile_dict, opp.eligibility or {})

        # 2. Semantic similarity
        semantic_sc = 0.5
        if opp.embedding:
            opp_emb_list = json.loads(opp.embedding) if isinstance(opp.embedding, str) else opp.embedding
            semantic_sc = max(0.0, cosine_similarity(profile_emb, opp_emb_list))
        else:
            # Lazy embed
            from app.ml.embed import build_opportunity_text
            opp_text = build_opportunity_text({
                "title": opp.title,
                "description": opp.description,
                "category": opp.category,
                "benefits": opp.benefits,
                "eligibility": opp.eligibility or {},
                "locations": opp.locations or [],
            })
            opp_emb = encode_text(opp_text)
            opp.embedding = json.dumps(opp_emb)
            await db.commit()
            semantic_sc = max(0.0, cosine_similarity(profile_emb, opp_emb))

        # 3. Geo score
        geo_sc = geo_score(profile_dict, opp_dict)

        # 4. Trust score
        trust_sc = opp.trust_score or 0.8

        # 5. Composite
        final_score = composite_score(rules_sc, semantic_sc, geo_sc, trust_sc)

        reason_list = reasons if reasons else ["General eligibility match"]

        item = RecoItem(
            opportunity=OpportunityOut.model_validate(opp),
            score=round(final_score * 100, 1),
            rules_score=round(rules_sc * 100, 1),
            semantic_score=round(semantic_sc * 100, 1),
            geo_score=round(geo_sc * 100, 1),
            trust_score=round(trust_sc * 100, 1),
            reasons=reason_list,
            eligibility_status=checks,
        )
        scored.append((final_score, item))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)
    top_items = [item for _, item in scored[:limit]]

    return RecoResponse(total=len(top_items), items=top_items)


@router.get("/public", response_model=RecoResponse)
async def get_public_recommendations(
    category: str | None = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Returns top opportunities without auth (for landing page preview)."""
    _, opps = await crud.list_opportunities(db, limit=limit, category=category)
    items = [
        RecoItem(
            opportunity=OpportunityOut.model_validate(opp),
            score=round(opp.trust_score * 100, 1),
            rules_score=50.0,
            semantic_score=50.0,
            geo_score=50.0,
            trust_score=round(opp.trust_score * 100, 1),
            reasons=["Popular scheme in Tamil Nadu"],
            eligibility_status={},
        )
        for opp in opps
    ]
    return RecoResponse(total=len(items), items=items)
