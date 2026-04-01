import asyncio
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models import Opportunity

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(func.count()).select_from(Opportunity))
        count = res.scalar()
        print(f"Total opportunities: {count}")
        
        # Check first 5
        res = await db.execute(select(Opportunity).limit(5))
        items = res.scalars().all()
        for item in items:
            print(f"- {item.title} ({item.category}) Active: {item.is_active}")

asyncio.run(check())
