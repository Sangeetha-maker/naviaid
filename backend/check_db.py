import asyncio, sys, logging
sys.path.insert(0, '.')
logging.disable(logging.CRITICAL)

from dotenv import load_dotenv
load_dotenv('../.env')

from app.database import AsyncSessionLocal, engine
from app.models import Base, Opportunity
from sqlalchemy import select, func

async def go():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        total = (await db.execute(select(func.count(Opportunity.id)))).scalar_one()
        by_cat = await db.execute(
            select(Opportunity.category, func.count(Opportunity.id))
            .group_by(Opportunity.category)
        )
        by_src = await db.execute(
            select(Opportunity.source, func.count(Opportunity.id))
            .group_by(Opportunity.source)
        )
        recent = await db.execute(
            select(Opportunity.title, Opportunity.category, Opportunity.source)
            .order_by(Opportunity.created_at.desc())
            .limit(10)
        )

    with open('db_summary.txt', 'w', encoding='ascii', errors='replace') as f:
        f.write(f"Total opportunities in DB: {total}\n\n")
        f.write("By Category:\n")
        for row in by_cat.all():
            f.write(f"  {row[0]:15s} : {row[1]}\n")
        f.write("\nBy Source:\n")
        for row in by_src.all():
            f.write(f"  {str(row[0])[:30]:30s} : {row[1]}\n")
        f.write("\nMost Recent 10 entries:\n")
        for row in recent.all():
            f.write(f"  [{row[1]:10s}] {str(row[0])[:70]}\n")

    await engine.dispose()
    print("done")

asyncio.run(go())
