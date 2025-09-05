# nano db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg2.connect(dsn)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wolfguard_users (
        id SERIAL PRIMARY KEY,
        telegram_id TEXT UNIQUE,
        wallet TEXT,
        plan TEXT,
        expiry TIMESTAMP
    );
    """)
    # example invoices table - optional
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id SERIAL PRIMARY KEY,
        tg_id TEXT,
        plan TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        paid BOOLEAN DEFAULT FALSE
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

def add_user(telegram_id, wallet, plan, expiry):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO wolfguard_users (telegram_id, wallet, plan, expiry)
    VALUES (%s,%s,%s,%s)
    ON CONFLICT (telegram_id) DO UPDATE
    SET wallet = EXCLUDED.wallet, plan = EXCLUDED.plan, expiry = EXCLUDED.expiry
    """, (telegram_id, wallet, plan, expiry))
    conn.commit()
    cur.close()
    conn.close()

def get_user(telegram_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM wolfguard_users WHERE telegram_id = %s", (telegram_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def mark_invoice_paid(invoice_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE invoices SET paid = TRUE WHERE id = %s", (invoice_id,))
    conn.commit()
    cur.close()
    conn.close()