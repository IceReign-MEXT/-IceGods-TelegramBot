import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Create invoices table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id SERIAL PRIMARY KEY,
        tg_id BIGINT NOT NULL,
        plan TEXT NOT NULL,
        price NUMERIC NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT NOW(),
        paid_at TIMESTAMP
    )
    """)

    # Create users table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wolfguard_users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE,
        wallet TEXT,
        plan TEXT,
        expiry TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()