CREATE TABLE IF NOT EXISTS wolfguard_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    wallet TEXT,
    plan TEXT,
    expiry TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT,
    plan TEXT,
    amount INT,
    paid BOOLEAN DEFAULT FALSE,
    created TIMESTAMP DEFAULT NOW()
);