import asyncio
import asyncpg
import sys

async def main():
    dsn = "postgresql://postgres:R7%26.V6Jeg9c96h4@db.oheflrxwqusnwmpglmqg.supabase.co:5432/postgres"
    print(f"Connecting to {dsn}")
    try:
        conn = await asyncpg.connect(dsn)
        print("Connected successfully!")
        await conn.close()
    except Exception as e:
        print(f"Error connecting: {e}")
        sys.exit(3)

asyncio.run(main())
