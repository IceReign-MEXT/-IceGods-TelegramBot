from db import init_db

init_db()  # ✅ auto-run migrations

import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from db import init_db, add_invoice, get_conn, mark_invoice_paid

# Load env vars
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = int(os.getenv("TELEGRAM_OWNER_ID"))
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# Updated prices 💰
PRICES = {
    "plan_1h": 5,
    "plan_4h": 15,
    "plan_8h": 25,
    "plan_12h": 40,
    "plan_24h": 70,
    "plan_week": 300,
    "plan_month": 1000,
    "plan_year": 8000
}

PAYMENT_WALLET_SOL = os.getenv("PAYMENT_WALLET_SOL")
PAYMENT_WALLET_ETH = os.getenv("PAYMENT_WALLET_ETH")

init_db()

async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome to IceGods Watcher!\nUse /plans to view subscription options.")

async def plans(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("1h - $5", callback_data="plan_1h"),
         InlineKeyboardButton("4h - $15", callback_data="plan_4h")],
        [InlineKeyboardButton("1d - $70", callback_data="plan_24h"),
         InlineKeyboardButton("1w - $300", callback_data="plan_week")],
        [InlineKeyboardButton("1m - $1000", callback_data="plan_month"),
         InlineKeyboardButton("1y - $8000", callback_data="plan_year")]
    ]
    await update.message.reply_text("📌 Choose a plan:", reply_markup=InlineKeyboardMarkup(keyboard))

async def plan_button(update: Update, context):
    q = update.callback_query
    await q.answer()
    plan = q.data
    price = PRICES.get(plan)

    payload = {"tg_id": update.effective_user.id, "plan": plan, "price": price}
    r = requests.post(f"{API_BASE}/api/create_invoice", json=payload)

    if r.status_code == 200:
        inv = r.json()
        msg = f"💸 Pay ${price} in USDC (Solana) to:\n\n`{PAYMENT_WALLET_SOL}`\n\nInvoice ID: {inv['id']}"
        await q.edit_message_text(msg, parse_mode="Markdown")
    else:
        await q.edit_message_text("❌ Failed to create invoice.")

async def sweep_cmd(update: Update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    await update.message.reply_text("🧹 Sweep triggered!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(CallbackQueryHandler(plan_button))
    app.add_handler(CommandHandler("sweep", sweep_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()