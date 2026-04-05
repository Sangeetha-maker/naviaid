import asyncio
import sys
import os

# Ensure app imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models import Base, User, UserProfile, Opportunity, Application
from app.database import create_pgvector_extension

sqlite_url = "sqlite+aiosqlite:///./naviaid.db"
pg_url = "postgresql+asyncpg://postgres:R7%26.V6Jeg9c96h4@db.oheflrxwqusnwmpglmqg.supabase.co:5432/postgres"

sqlite_engine = create_async_engine(sqlite_url)
pg_engine = create_async_engine(pg_url, pool_pre_ping=True)

async def migrate():
    print("Initiating migration to Supabase...")
    
    # Extract data from SQLite FIRST
    print("Extracting data from local SQLite database...")
    sqlite_session = sessionmaker(bind=sqlite_engine, class_=AsyncSession)()
    
    users = (await sqlite_session.execute(select(User))).scalars().all()
    profiles = (await sqlite_session.execute(select(UserProfile))).scalars().all()
    opps = (await sqlite_session.execute(select(Opportunity))).scalars().all()
    apps = (await sqlite_session.execute(select(Application))).scalars().all()

    await sqlite_session.close()

    print(f"Found: {len(users)} users, {len(profiles)} profiles, {len(opps)} opportunities, {len(apps)} applications.")

    print("Connecting to Postgres & Rebuilding tables...")
    async with pg_engine.begin() as conn:
        try:
            await create_pgvector_extension(conn)
        except Exception as e:
            pass
            
        print("Dropping existing tables to do a fresh migration...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Tables re-created in Postgres.")

    # Insert into Postgres
    print("Transferring data to Supabase...")
    pg_session_maker = sessionmaker(bind=pg_engine, class_=AsyncSession)
    async with pg_session_maker() as pg_session:
        for u in users:
            new_u = User(**{c.name: getattr(u, c.name) for c in User.__table__.columns})
            pg_session.add(new_u)
            
        for p in profiles:
            new_p = UserProfile(**{c.name: getattr(p, c.name) for c in UserProfile.__table__.columns})
            pg_session.add(new_p)
            
        for o in opps:
            new_o = Opportunity(**{c.name: getattr(o, c.name) for c in Opportunity.__table__.columns})
            pg_session.add(new_o)
            
        for a in apps:
            new_a = Application(**{c.name: getattr(a, c.name) for c in Application.__table__.columns})
            pg_session.add(new_a)
            
        await pg_session.commit()
    
    print("Migration complete! Supabase database is securely populated.")
    
    await sqlite_engine.dispose()
    await pg_engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
