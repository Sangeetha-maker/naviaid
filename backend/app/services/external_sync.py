"""
NaviAid External Sync Service
Fetches live jobs, scholarships, and government schemes from:
  - JSearch (RapidAPI) – real-time jobs from Indeed/LinkedIn/Google Jobs
  - Adzuna – jobs from India job boards
  - MyScheme.gov.in – central government schemes (internal JSON endpoint)
  - TNPSC RSS – Tamil Nadu public service commission notifications
  - Employment News RSS – central govt job notifications

All results are upserted into the `opportunities` table by source_url (no duplicates).
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx
import feedparser
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Opportunity
from app.config import settings

logger = logging.getLogger("naviaid.sync")


def _gen_uuid() -> str:
    return str(uuid.uuid4())


async def _upsert_opportunity(db: AsyncSession, data: dict) -> bool:
    """
    Insert if source_url not seen before, else skip.
    Returns True if newly inserted.
    """
    source_url = data.get("source_url") or data.get("apply_url") or ""
    if source_url:
        existing = await db.execute(
            select(Opportunity).where(Opportunity.source_url == source_url)
        )
        if existing.scalar_one_or_none():
            return False  # already exists

    opp = Opportunity(
        id=_gen_uuid(),
        title=data.get("title", "Untitled")[:499],
        description=data.get("description", "")[:4999],
        category=data.get("category", "job"),
        subcategory=data.get("subcategory"),
        source=data.get("source"),
        source_url=source_url[:999] if source_url else None,
        apply_url=data.get("apply_url", source_url)[:999] if data.get("apply_url") or source_url else None,
        eligibility=data.get("eligibility", {}),
        documents_required=data.get("documents_required", []),
        benefits=data.get("benefits"),
        amount=data.get("amount"),
        deadline=data.get("deadline"),
        is_recurring=data.get("is_recurring", False),
        locations=data.get("locations", ["Tamil Nadu"]),
        is_pan_india=data.get("is_pan_india", False),
        trust_score=data.get("trust_score", 0.75),
        is_active=True,
    )
    db.add(opp)
    return True


# ─────────────────────────────────────────────────────────────
#  1. JSearch via RapidAPI
# ─────────────────────────────────────────────────────────────

async def sync_jsearch(db: AsyncSession) -> dict:
    """Fetch jobs from JSearch (aggregates Google Jobs, Indeed, LinkedIn)."""
    key = settings.RAPIDAPI_KEY
    if not key:
        return {"synced": 0, "error": "RAPIDAPI_KEY not set"}

    queries = [
        "government jobs Tamil Nadu",
        "jobs Chennai India",
        "TNPSC recruitment",
        "scholarship Tamil Nadu student",
    ]

    synced = 0
    errors = []
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        for query in queries:
            try:
                resp = await client.get(
                    "https://jsearch.p.rapidapi.com/search",
                    headers=headers,
                    params={
                        "query": query,
                        "page": "1",
                        "num_pages": "1",
                        "country": "in",
                        "date_posted": "week",
                    },
                )
                resp.raise_for_status()
                jobs = resp.json().get("data", [])

                for job in jobs:
                    # Determine category
                    title_lower = (job.get("job_title") or "").lower()
                    if any(w in title_lower for w in ["scholarship", "fellowship", "grant"]):
                        cat = "scholarship"
                    elif any(w in title_lower for w in ["training", "course", "skill"]):
                        cat = "upskill"
                    else:
                        cat = "job"

                    employer = job.get("employer_name", "")
                    city = job.get("job_city") or ""
                    state = job.get("job_state") or "Tamil Nadu"
                    location = f"{city}, {state}".strip(", ")

                    desc = job.get("job_description") or job.get("job_highlights", {})
                    if isinstance(desc, dict):
                        parts = []
                        for k, v in desc.items():
                            if isinstance(v, list):
                                parts.append(f"{k}: " + "; ".join(v))
                        desc = " | ".join(parts) or "See job posting for details."

                    inserted = await _upsert_opportunity(db, {
                        "title": f"{job.get('job_title', 'Job Opening')} – {employer}",
                        "description": str(desc)[:4999],
                        "category": cat,
                        "subcategory": employer,
                        "source": "JSearch / Google Jobs",
                        "source_url": job.get("job_apply_link") or job.get("job_google_link"),
                        "apply_url": job.get("job_apply_link") or job.get("job_google_link"),
                        "locations": [location] if location else ["Tamil Nadu"],
                        "deadline": job.get("job_offer_expiration_datetime_utc"),
                        "eligibility": {
                            "employment_type": job.get("job_employment_type", ""),
                            "experience_required": job.get("job_required_experience", {}).get("required_experience_in_months"),
                        },
                        "trust_score": 0.80,
                    })
                    if inserted:
                        synced += 1

            except Exception as e:
                logger.warning(f"JSearch query '{query}' failed: {e}")
                errors.append(str(e))

    await db.commit()
    return {"synced": synced, "errors": errors}


# ─────────────────────────────────────────────────────────────
#  2. Adzuna Jobs API
# ─────────────────────────────────────────────────────────────

async def sync_adzuna(db: AsyncSession) -> dict:
    """Fetch jobs from Adzuna India."""
    app_id = settings.ADZUNA_APP_ID
    app_key = settings.ADZUNA_APP_KEY
    if not app_id or not app_key:
        return {"synced": 0, "error": "ADZUNA credentials not set"}

    queries = ["government jobs Tamil Nadu", "Chennai software developer", "manufacturing jobs Tamil Nadu"]
    synced = 0
    errors = []

    async with httpx.AsyncClient(timeout=20) as client:
        for query in queries:
            try:
                resp = await client.get(
                    f"https://api.adzuna.com/v1/api/jobs/in/search/1",
                    params={
                        "app_id": app_id,
                        "app_key": app_key,
                        "results_per_page": 20,
                        "what": query,
                        "where": "Tamil Nadu",
                        "content-type": "application/json",
                    },
                )
                resp.raise_for_status()
                jobs = resp.json().get("results", [])

                for job in jobs:
                    cat_label = (job.get("category", {}).get("label") or "").lower()
                    if "it" in cat_label or "software" in cat_label:
                        cat = "job"
                    elif "edu" in cat_label or "teach" in cat_label:
                        cat = "upskill"
                    else:
                        cat = "job"

                    location = job.get("location", {}).get("display_name", "Tamil Nadu")
                    company = job.get("company", {}).get("display_name", "")

                    inserted = await _upsert_opportunity(db, {
                        "title": f"{job.get('title', 'Job')} – {company}".strip(" –"),
                        "description": job.get("description", "See Adzuna for details.")[:4999],
                        "category": cat,
                        "subcategory": company,
                        "source": "Adzuna",
                        "source_url": job.get("redirect_url"),
                        "apply_url": job.get("redirect_url"),
                        "locations": [location],
                        "deadline": job.get("contract_time"),
                        "eligibility": {
                            "salary_min": job.get("salary_min"),
                            "salary_max": job.get("salary_max"),
                            "contract_type": job.get("contract_type"),
                        },
                        "trust_score": 0.82,
                    })
                    if inserted:
                        synced += 1

            except Exception as e:
                logger.warning(f"Adzuna query '{query}' failed: {e}")
                errors.append(str(e))

    await db.commit()
    return {"synced": synced, "errors": errors}


# ─────────────────────────────────────────────────────────────
#  3. MyScheme.gov.in (internal JSON search endpoint)
# ─────────────────────────────────────────────────────────────

MYSCHEME_CATEGORIES = [
    "Education & Learning",
    "Health & Wellness",
    "Agriculture,Rural & Environment",
    "Banking,Financial Services and Insurance",
    "Business & Entrepreneurship",
    "Housing & Shelter",
    "Science, IT & Communications",
    "Skills & Employment",
    "Social welfare & Empowerment",
    "Sports & Culture",
    "Transport & Infrastructure",
    "Travel & Tourism",
    "Utility & Sanitation",
    "Women and Child",
]

CATEGORY_MAP = {
    "Education & Learning": "scholarship",
    "Health & Wellness": "health",
    "Skills & Employment": "job",
    "Business & Entrepreneurship": "upskill",
    "Women and Child": "government",
}


async def sync_myscheme(db: AsyncSession) -> dict:
    """Fetch government schemes from MyScheme.gov.in public search API."""
    synced = 0
    errors = []

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.myscheme.gov.in",
        "Referer": "https://www.myscheme.gov.in/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }

    states_to_fetch = ["Tamil Nadu", "All India"]

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for state in states_to_fetch:
            try:
                resp = await client.get(
                    "https://www.myscheme.gov.in/api/v1/scheme/search",
                    headers=headers,
                    params={
                        "keyword": "",
                        "state": state,
                        "page": 1,
                        "limit": 50,
                        "lang": "en",
                    },
                )
                if resp.status_code != 200:
                    # Try alternate endpoint format
                    resp = await client.post(
                        "https://www.myscheme.gov.in/api/v1/scheme/filter",
                        headers=headers,
                        json={
                            "state": [state] if state != "All India" else [],
                            "keyword": "",
                            "page": 1,
                            "limit": 40,
                        },
                    )

                if resp.status_code != 200:
                    errors.append(f"MyScheme {state}: HTTP {resp.status_code}")
                    continue

                data = resp.json()
                schemes = data.get("data", data.get("schemes", data.get("result", [])))
                if isinstance(schemes, dict):
                    schemes = schemes.get("data", [])

                for scheme in schemes:
                    title = scheme.get("schemeName") or scheme.get("name") or scheme.get("title") or ""
                    if not title:
                        continue

                    category_raw = scheme.get("category") or scheme.get("categories", [""])[0] if scheme.get("categories") else ""
                    if isinstance(category_raw, dict):
                        category_raw = category_raw.get("name", "")
                    cat = CATEGORY_MAP.get(str(category_raw), "government")

                    desc = scheme.get("schemeShortDescription") or scheme.get("description") or scheme.get("shortDesc") or "See MyScheme.gov.in for details."
                    slug = scheme.get("slug") or scheme.get("schemeId") or ""
                    apply_url = f"https://www.myscheme.gov.in/schemes/{slug}" if slug else "https://www.myscheme.gov.in"

                    min_age = scheme.get("minAge") or (scheme.get("eligibility") or {}).get("minAge")
                    max_age = scheme.get("maxAge") or (scheme.get("eligibility") or {}).get("maxAge")
                    gender = scheme.get("gender") or (scheme.get("eligibility") or {}).get("gender")
                    max_income = scheme.get("annualIncome") or (scheme.get("eligibility") or {}).get("annualIncome")

                    inserted = await _upsert_opportunity(db, {
                        "title": str(title)[:499],
                        "description": str(desc)[:4999],
                        "category": cat,
                        "source": "MyScheme.gov.in",
                        "source_url": apply_url,
                        "apply_url": apply_url,
                        "locations": [state] if state != "All India" else [],
                        "is_pan_india": state == "All India",
                        "is_recurring": True,
                        "eligibility": {
                            "min_age": min_age,
                            "max_age": max_age,
                            "gender": gender,
                            "max_income": max_income,
                        },
                        "trust_score": 0.95,  # govt source = high trust
                    })
                    if inserted:
                        synced += 1

            except Exception as e:
                logger.warning(f"MyScheme sync ({state}) failed: {e}")
                errors.append(str(e))

    await db.commit()
    return {"synced": synced, "errors": errors}


# ─────────────────────────────────────────────────────────────
#  4. RSS Feeds (TNPSC + Employment News)
# ─────────────────────────────────────────────────────────────

RSS_FEEDS = [
    {
        "url": "https://www.tnpsc.gov.in/rss.xml",
        "source": "TNPSC",
        "category": "job",
        "locations": ["Tamil Nadu"],
        "trust_score": 0.95,
    },
    {
        "url": "https://www.employmentnews.gov.in/RSS/rss_feed.xml",
        "source": "Employment News",
        "category": "job",
        "locations": [],
        "is_pan_india": True,
        "trust_score": 0.90,
    },
    {
        "url": "https://www.tn.gov.in/rss.xml",
        "source": "TN Government Portal",
        "category": "government",
        "locations": ["Tamil Nadu"],
        "trust_score": 0.92,
    },
]


async def sync_rss_feeds(db: AsyncSession) -> dict:
    """Parse RSS feeds and insert new entries as opportunities."""
    synced = 0
    errors = []

    for feed_cfg in RSS_FEEDS:
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(
                    feed_cfg["url"],
                    headers={"User-Agent": "NaviAid/1.0 (+https://naviaid.in)"},
                )
            parsed = feedparser.parse(resp.text)
            entries = parsed.entries[:30]  # cap at 30 per feed

            for entry in entries:
                title = getattr(entry, "title", "") or ""
                link = getattr(entry, "link", "") or ""
                summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
                published = getattr(entry, "published", None)

                if not title:
                    continue

                inserted = await _upsert_opportunity(db, {
                    "title": str(title)[:499],
                    "description": str(summary)[:4999] or f"See {feed_cfg['source']} for full details.",
                    "category": feed_cfg["category"],
                    "source": feed_cfg["source"],
                    "source_url": link,
                    "apply_url": link,
                    "locations": feed_cfg.get("locations", []),
                    "is_pan_india": feed_cfg.get("is_pan_india", False),
                    "deadline": published,
                    "is_recurring": False,
                    "trust_score": feed_cfg["trust_score"],
                })
                if inserted:
                    synced += 1

        except Exception as e:
            logger.warning(f"RSS feed {feed_cfg['url']} failed: {e}")
            errors.append(f"{feed_cfg['source']}: {str(e)}")

    await db.commit()
    return {"synced": synced, "errors": errors}


# ─────────────────────────────────────────────────────────────
#  Master sync runner
# ─────────────────────────────────────────────────────────────

async def run_full_sync(db: AsyncSession) -> dict:
    """Run all sync sources and return a summary."""
    logger.info("Starting full external data sync...")
    results = {}

    results["jsearch"] = await sync_jsearch(db)
    results["adzuna"] = await sync_adzuna(db)
    results["myscheme"] = await sync_myscheme(db)
    results["rss"] = await sync_rss_feeds(db)

    total_synced = sum(r.get("synced", 0) for r in results.values())
    all_errors = [e for r in results.values() for e in r.get("errors", [])]

    logger.info(f"Sync complete: {total_synced} new opportunities added.")
    return {
        "total_synced": total_synced,
        "sources": results,
        "errors": all_errors,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
