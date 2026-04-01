import asyncio
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models import Opportunity

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Opportunity.category, func.count(Opportunity.id)).group_by(Opportunity.category))
        rows = res.all()
        print("Categories in database:")
        for cat, count in rows:
            print(f"- {cat}: {count}")

asyncio.run(check())
