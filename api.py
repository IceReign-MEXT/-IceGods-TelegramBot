# api.py
import os
import uuid
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
USDC_SOLANA_EXPLORER = "https://api.mainnet-beta.solana.com"

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route("/api/create_invoice", methods=["POST"])
def create_invoice():
    data = request.get_json()
    tg_id = data.get("tg_id")
    plan = data.get("plan")
    price = data.get("price")
    wallet = data.get("wallet")

    if not tg_id or not plan or not price:
        return jsonify({"error": "missing fields"}), 400

    invoice_id = str(uuid.uuid4())

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO invoices (id, telegram_id, plan, amount, wallet, status) VALUES (%s, %s, %s, %s, %s, %s)",
        (invoice_id, tg_id, plan, price, wallet, "pending"),
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"invoice_id": invoice_id, "wallet": wallet})

@app.route("/api/verify_tx", methods=["POST"])
def verify_tx():
    data = request.get_json()
    tx = data.get("tx")
    invoice_id = data.get("invoice_id")

    if not tx or not invoice_id:
        return jsonify({"error": "missing tx or invoice"}), 400

    # TODO: Replace with real Solana/Ethereum explorer API check
    # For now, simulate transaction found
    paid = True  

    if paid:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE invoices SET status='paid' WHERE id=%s", (invoice_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "paid"})
    else:
        return jsonify({"status": "unconfirmed"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))