"""
NaviAid FastAPI Application – main entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from app.config import settings
from app.database import engine, create_pgvector_extension, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Base
from app.routers import auth, reco, search, admin, profile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("naviaid")

# ──────────────────── Rate Limiter ────────────────────────────

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables & auto-sync free data sources."""
    logger.info("Starting NaviAid API...")
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: None)  # warmup
        try:
            await create_pgvector_extension(conn)
        except Exception as e:
            logger.warning(f"pgvector extension: {e}")
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database ready.")

    # Auto-seed free data sources on startup (RSS + MyScheme – no API keys needed)
    import asyncio
    from app.database import AsyncSessionLocal
    from app.services.external_sync import sync_rss_feeds, sync_myscheme

    async def _background_seed():
        try:
            async with AsyncSessionLocal() as db:
                logger.info("Auto-syncing RSS feeds...")
                r1 = await sync_rss_feeds(db)
                logger.info(f"RSS sync: {r1.get('synced', 0)} new items")
                r2 = await sync_myscheme(db)
                logger.info(f"MyScheme sync: {r2.get('synced', 0)} new items")
        except Exception as e:
            logger.warning(f"Background seed failed: {e}")

    asyncio.ensure_future(_background_seed())
    yield
    logger.info("Shutting down NaviAid API.")
    await engine.dispose()


# ──────────────────── App ─────────────────────────────────────

app = FastAPI(
    title="NaviAid API",
    description="AI-powered government scheme discovery for Tamil Nadu's underserved communities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS – allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────── Routers ─────────────────────────────────

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(reco.router)
app.include_router(search.router)
app.include_router(admin.router)


# ──────────────────── Health ──────────────────────────────────

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": "1.0.0", "service": "NaviAid API"}


@app.post("/sync", tags=["sync"])
async def manual_sync(db: AsyncSession = Depends(get_db)):
    """Manually trigger RSS + MyScheme sync (no auth required). Useful for local dev."""
    from app.services.external_sync import sync_rss_feeds, sync_myscheme
    r1 = await sync_rss_feeds(db)
    r2 = await sync_myscheme(db)
    return {
        "rss": r1,
        "myscheme": r2,
        "total_synced": r1.get("synced", 0) + r2.get("synced", 0),
    }


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to NaviAid API",
        "docs": "/docs",
        "health": "/health",
    }
