import os
import logging
import psycopg2
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DATABASE_URL")

# Plans
PLANS = {
    "starter": {"price": 10, "days": 7},
    "pro": {"price": 30, "days": 30},
    "godmode": {"price": 200, "days": 9999},  # lifetime
}

# Connect DB
def get_db():
    return psycopg2.connect(DB_URL)

# Create tables if not exist
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wolfguard_users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE,
        wallet TEXT,
        plan TEXT,
        expiry TIMESTAMP
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT,
        plan TEXT,
        amount INT,
        paid BOOLEAN DEFAULT FALSE,
        created TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Starter - $10 (7 days)", callback_data="starter")],
        [InlineKeyboardButton("Pro - $30 (30 days)", callback_data="pro")],
        [InlineKeyboardButton("God Mode - $200 (Lifetime)", callback_data="godmode")]
    ]
    await update.message.reply_text(
        "👋 Welcome to IceGods Bot!\nChoose your plan:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = query.data
    amount = PLANS[plan]["price"]

    # Save invoice
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO invoices (telegram_id, plan, amount) VALUES (%s,%s,%s) RETURNING id",
        (query.from_user.id, plan, amount)
    )
    invoice_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    await query.edit_message_text(
        text=f"💳 Pay ${amount} for {plan.title()}.\n"
             f"Send crypto to wallet:\n\n"
             f"`{os.getenv('WALLET_ADDRESS')}`\n\n"
             f"Then wait for confirmation (Invoice #{invoice_id}).",
        parse_mode="Markdown"
    )

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()