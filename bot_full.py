# nano bot_full.py
import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from db import init_db, get_conn, add_user, get_user, mark_invoice_paid

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing in environment")

OWNER_ID = int(os.getenv("TELEGRAM_OWNER_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # set in Railway when using webhook
PORT = int(os.getenv("PORT", 5000))
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# prices example (adjust if needed)
PRICES = {
    "plan_1h": 1,
    "plan_4h": 3,
    "plan_24h": 10,
    "plan_week": 50,
    "plan_month": 150,
}

PAYMENT_WALLET_SOL = os.getenv("PAYMENT_WALLET_SOL")
PAYMENT_WALLET_ETH = os.getenv("PAYMENT_WALLET_ETH")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome. Use /plans to see subscription plans.")

async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1h - $1", callback_data="plan_1h"),
            InlineKeyboardButton("4h - $3", callback_data="plan_4h"),
        ],
        [
            InlineKeyboardButton("1d - $10", callback_data="plan_24h"),
            InlineKeyboardButton("weekly - $50", callback_data="plan_week"),
        ],
    ]
    await update.message.reply_text("Choose a plan:", reply_markup=InlineKeyboardMarkup(keyboard))

async def plan_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    plan = q.data
    price = PRICES.get(plan, None)
    if price is None:
        await q.edit_message_text("Plan not found.")
        return
    # create invoice via API (if you have an API) or show payment address
    msg = f"💸 Pay ${price} in USDC(Solana) to:\n{PAYMENT_WALLET_SOL}\n\nReply here with the TX hash when done."
    await q.edit_message_text(msg)

async def tx_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    # call your verification API or implement verification logic here
    try:
        r = requests.post(f"{API_BASE}/api/verify_tx", json={"tx": txt}, timeout=15)
        ok = r.json().get("ok", False)
    except Exception:
        ok = False

    if ok:
        # example: mark latest invoice for user as paid
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM invoices WHERE tg_id = %s ORDER BY created_at DESC LIMIT 1", (update.effective_user.id,))
        row = cur.fetchone()
        if row:
            mark_invoice_paid(row[0])
        await update.message.reply_text("✅ Payment verified! You are active.")
    else:
        await update.message.reply_text("❌ Could not verify the payment. Ensure TX hash is correct.")

async def sweep_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    await update.message.reply_text("🧹 Sweep started (owner-only) — implement your sweep logic here.")

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plans", plans))
    app.add_handler(CallbackQueryHandler(plan_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tx_listener))
    app.add_handler(CommandHandler("sweep", sweep_cmd))

    # If WEBHOOK_URL is set (Production on Railway), use webhook; otherwise fallback to polling for local test
    if WEBHOOK_URL:
        print("Starting webhook mode...")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        )
    else:
        print("Starting polling mode (local test)...")
        app.run_polling()

if __name__ == "__main__":
    main()