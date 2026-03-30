"""
NaviAid - Standalone Sync Runner
Run all external API data fetches (RSS, MyScheme, JSearch, Adzuna) directly.

Usage:
    python run_sync.py              # run all available syncs
    python run_sync.py --rss        # RSS only
    python run_sync.py --myscheme   # MyScheme only
    python run_sync.py --jsearch    # JSearch only (needs RAPIDAPI_KEY in .env)
    python run_sync.py --adzuna     # Adzuna only (needs ADZUNA_APP_ID/KEY in .env)
"""

import asyncio
import sys
import io

# Force UTF-8 stdout so we don't get encoding errors on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from pathlib import Path

# make sure app/ is importable from backend/
sys.path.insert(0, str(Path(__file__).parent))

# load .env from project root or backend/
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent / ".env")

from app.database import AsyncSessionLocal, engine
from app.models import Base
from app.services.external_sync import (
    sync_rss_feeds,
    sync_myscheme,
    sync_jsearch,
    sync_adzuna,
    run_full_sync,
)
from app.config import settings


async def ensure_tables():
    """Create all DB tables if not present."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def _pprint(name: str, result: dict):
    print(f"\n{'=' * 60}")
    print(f"  SOURCE: {name}")
    print(f"{'=' * 60}")
    synced = result.get("synced", result.get("total_synced", 0))
    errors = result.get("errors", [])
    print(f"  New items synced : {synced}")
    if errors:
        print(f"  Errors ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("  No errors.")
    if "sources" in result:
        print("\n  Sub-source breakdown:")
        for src, r in result["sources"].items():
            s = r.get("synced", 0)
            e = r.get("errors", [])
            err_note = "" if not e else f" | ERRORS: {'; '.join(e[:2])}"
            print(f"    [{src:12s}]  {s} new items{err_note}")


async def main():
    args = set(sys.argv[1:])
    run_all = not args

    print("=" * 60)
    print("  NaviAid External Data Sync")
    print(f"  Database : {settings.DATABASE_URL}")
    print(f"  RapidAPI : {'SET' if settings.RAPIDAPI_KEY else 'NOT SET (JSearch skipped)'}")
    print(f"  Adzuna   : {'SET' if settings.ADZUNA_APP_ID else 'NOT SET (Adzuna skipped)'}")
    print("=" * 60)

    print("\n[*] Ensuring database tables exist...")
    await ensure_tables()
    print("    Done.\n")

    async with AsyncSessionLocal() as db:

        if run_all:
            print("[*] Running FULL sync (all sources)...")
            result = await run_full_sync(db)
            _pprint("FULL SYNC SUMMARY", result)

        else:
            if "--rss" in args:
                print("[*] Syncing RSS feeds (TNPSC, Employment News, TN Gov)...")
                r = await sync_rss_feeds(db)
                _pprint("RSS Feeds", r)

            if "--myscheme" in args:
                print("[*] Syncing MyScheme.gov.in...")
                r = await sync_myscheme(db)
                _pprint("MyScheme.gov.in", r)

            if "--jsearch" in args:
                if not settings.RAPIDAPI_KEY:
                    print("[!] RAPIDAPI_KEY not set - skipping JSearch.")
                else:
                    print("[*] Syncing JSearch (Google Jobs / LinkedIn / Indeed)...")
                    r = await sync_jsearch(db)
                    _pprint("JSearch", r)

            if "--adzuna" in args:
                if not settings.ADZUNA_APP_ID:
                    print("[!] ADZUNA_APP_ID not set - skipping Adzuna.")
                else:
                    print("[*] Syncing Adzuna India jobs...")
                    r = await sync_adzuna(db)
                    _pprint("Adzuna", r)

    print("\n" + "=" * 60)
    print("  Sync complete!")
    print("=" * 60 + "\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
