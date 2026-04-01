import asyncio
import logging
import sys
from os.path import dirname, join

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("naviaid.manual_sync")

# Fix path
sys.path.insert(0, dirname(__file__))

# Import apps
from app.database import AsyncSessionLocal
from app.services.external_sync import sync_myscheme, sync_rss_feeds

async def main():
    logger.info("Starting manual real-time sync for MyScheme and RSS feeds...")
    async with AsyncSessionLocal() as db:
        try:
            # Sync MyScheme
            myscheme_res = await sync_myscheme(db)
            logger.info(f"MyScheme sync complete. Synced: {myscheme_res.get('synced', 0)}")
            if myscheme_res.get("errors"):
                logger.error(f"MyScheme errors: {myscheme_res['errors']}")
            
            # Sync RSS
            rss_res = await sync_rss_feeds(db)
            logger.info(f"RSS sync complete. Synced: {rss_res.get('synced', 0)}")
            if rss_res.get("errors"):
                logger.error(f"RSS errors: {rss_res['errors']}")
                
            await db.commit()
            logger.info("Database committed successfully.")
            
        except Exception as e:
            logger.exception(f"Sync failed: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(main())
