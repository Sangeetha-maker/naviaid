"""
NaviAid Search Router – BM25 full-text + cosine vector hybrid search.
GET /search/?q=... returns matched opportunities.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.schemas import SearchResponse, OpportunityOut
from app.ml.embed import encode_text, cosine_similarity, build_opportunity_text

router = APIRouter(prefix="/search", tags=["search"])


def _parse_nl_query(q: str) -> dict:
    """Simple NL query parser to extract gender, location, income, category hints."""
    q_lower = q.lower()
    hints = {}

    # Gender hints
    if any(w in q_lower for w in ["girl", "female", "women", "woman", "lady"]):
        hints["gender"] = "F"
    elif any(w in q_lower for w in ["boy", "male", "man", "men"]):
        hints["gender"] = "M"

    # Category hints
    if any(w in q_lower for w in ["scholarship", "study", "education", "student"]):
        hints["category"] = "scholarship"
    elif any(w in q_lower for w in ["job", "employment", "work", "career"]):
        hints["category"] = "job"
    elif any(w in q_lower for w in ["skill", "training", "course", "learn"]):
        hints["category"] = "upskill"
    elif any(w in q_lower for w in ["health", "hospital", "medical", "treatment"]):
        hints["category"] = "health"
    elif any(w in q_lower for w in ["ngo", "welfare", "support", "assistance"]):
        hints["category"] = "ngo"

    # Income hints (e.g., "under 2L", "below 200000")
    import re
    income_match = re.search(r"under\s*(\d+(?:\.\d+)?)\s*l", q_lower)
    if income_match:
        hints["max_income"] = int(float(income_match.group(1)) * 100000)

    return hints


@router.get("/", response_model=SearchResponse)
async def search_opportunities(
    q: str | None = Query(None, max_length=500),
    category: str | None = None,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Hybrid search: full-text BM25 via PostgreSQL tsvector + vector cosine fallback.
    If no query is provided, it returns recent/popular opportunities.
    """
    if not q:
        total, items = await crud.list_opportunities(db, limit=limit, offset=offset, category=category)
        return SearchResponse(
            total=total,
            query="",
            items=[OpportunityOut.model_validate(o) for o in items],
        )
    hints = _parse_nl_query(q)
    effective_category = category or hints.get("category")

    # 1. BM25 full-text search
    ft_results = await crud.full_text_search_opportunities(db, q, limit=limit * 2)

    # 2. Vector search
    q_emb = encode_text(q)
    vec_results = await crud.vector_search_opportunities(db, q_emb, limit=limit * 2)

    # Merge: full-text gets priority, then add vector results not already included
    seen_ids: set[str] = set()
    merged: list = []

    for opp in ft_results:
        if opp.id not in seen_ids:
            seen_ids.add(opp.id)
            merged.append(opp)

    for opp, sim in vec_results:
        if opp.id not in seen_ids and sim > 0.3:
            seen_ids.add(opp.id)
            merged.append(opp)

    # Apply category + income filter from NL hints
    filtered = []
    for opp in merged:
        if effective_category and opp.category != effective_category:
            continue
        max_inc = hints.get("max_income")
        if max_inc is not None:
            opp_max_income = (opp.eligibility or {}).get("max_income")
            if opp_max_income is not None and opp_max_income > max_inc:
                continue
        gender_hint = hints.get("gender")
        if gender_hint:
            elig_gender = (opp.eligibility or {}).get("gender")
            if elig_gender and gender_hint not in elig_gender:
                continue
        filtered.append(opp)

    # Fallback: if no results, return popular opportunities
    if not filtered:
        _, filtered = await crud.list_opportunities(db, limit=limit, category=effective_category)

    paginated = filtered[offset: offset + limit]

    return SearchResponse(
        total=len(filtered),
        query=q,
        items=[OpportunityOut.model_validate(o) for o in paginated],
    )
