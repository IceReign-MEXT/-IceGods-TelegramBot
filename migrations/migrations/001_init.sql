CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    wallet TEXT,
    plan TEXT,
    expiry TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT NOT NULL,
    plan TEXT NOT NULL,
    price NUMERIC NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);