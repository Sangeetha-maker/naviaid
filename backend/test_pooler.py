import asyncio
import asyncpg
import sys

async def main():
    dsn = "postgresql://postgres.oheflrxwqusnwmpglmqg:R7%26.V6Jeg9c96h4@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
    print(f"Connecting to pooler")
    try:
        conn = await asyncpg.connect(dsn)
        print("Connected to pooler successfully!")
        await conn.close()
    except Exception as e:
        print(f"Error connecting: {type(e)} {e}")

asyncio.run(main())
