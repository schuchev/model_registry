# app/db.py
import os
import asyncpg
import asyncio

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_conn(retries: int = 15, delay: int = 2):

    last_exc = None
    for i in range(retries):
        try:
            conn = await asyncpg.connect(DATABASE_URL)
            print(f"[DB] Connected to database on attempt {i+1}")
            return conn
        except Exception as e:
            last_exc = e
            print(f"[DB] Database not ready, waiting {delay}s... (attempt {i+1}/{retries})")
            await asyncio.sleep(delay)
    raise Exception(f"[DB] Could not connect to database: {last_exc}")

async def init_db():

    conn = await get_conn()
    try:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'ml_engineer'
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            created_by INT REFERENCES users(id)
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS model_versions (
            id SERIAL PRIMARY KEY,
            model_id INT REFERENCES models(id),
            version_number INT NOT NULL,
            stage TEXT DEFAULT 'development',
            artifact_uri TEXT,
            metrics JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            created_by INT REFERENCES users(id),
            UNIQUE(model_id, version_number)
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            entity_type TEXT,
            entity_id INT,
            action TEXT,
            performed_by INT REFERENCES users(id),
            timestamp TIMESTAMP DEFAULT NOW()
        );
        """)
        print("[DB] Database initialized successfully")
    finally:
        await conn.close()