import asyncio
import json
from app.database import AsyncSessionLocal
from app.models import User, UserProfile
from app.routers.reco import get_recommendations
from sqlalchemy import select

async def test_reco():
    async with AsyncSessionLocal() as db:
        # Get a user (e.g., the admin)
        res = await db.execute(select(User).limit(1))
        user = res.scalar()
        if not user:
            print("No users found")
            return
        
        print(f"Testing recommendations for user: {user.email}")
        
        try:
            recos = await get_recommendations(limit=10, current_user=user, db=db)
            print(f"Total recommendations returned: {len(recos.items)}")
            for i, item in enumerate(recos.items):
                print(f"{i+1}. {item.opportunity.title} (Score: {item.score})")
        except Exception as e:
            print(f"Error in reco: {e}")
            import traceback
            traceback.print_exc()

asyncio.run(test_reco())
