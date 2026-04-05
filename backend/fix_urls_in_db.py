"""
Fix broken/wrong URLs directly in the production database.
Run: python fix_urls_in_db.py
"""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import update, text
from app.config import settings
from app.models import Opportunity

# Map of old URL -> new URL  (both source_url and apply_url)
URL_FIXES = {
    "https://pudumaipenn.tn.gov.in":        "https://tnscholarship.akara.co.in/index.php",
    "https://pudhumaipenn.tn.gov.in":       "https://tnscholarship.akara.co.in/index.php",
    "https://emis.tn.gov.in":               "https://emis.tnschools.gov.in",
    "https://adwelfare.tn.gov.in":          "https://adtw.tn.gov.in",
    "https://www.tnhb.gov.in":              "https://tnhb.tn.gov.in",
}

async def fix():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as db:
        total = 0
        for old_url, new_url in URL_FIXES.items():
            # Fix source_url
            r1 = await db.execute(
                update(Opportunity)
                .where(Opportunity.source_url == old_url)
                .values(source_url=new_url)
            )
            # Fix apply_url
            r2 = await db.execute(
                update(Opportunity)
                .where(Opportunity.apply_url == old_url)
                .values(apply_url=new_url)
            )
            changed = r1.rowcount + r2.rowcount
            if changed:
                print(f"✓ Updated {changed} row(s): {old_url} → {new_url}")
                total += changed

        await db.commit()
        print(f"\n✅ Done! {total} total rows updated in production DB.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix())
