import os
import uuid
import psycopg2
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    return {"status": "ok", "msg": "IceGods API running"}

# ✅ Create Invoice
@app.route("/api/create_invoice", methods=["POST"])
def create_invoice():
    data = request.get_json()
    tg_id = data.get("tg_id")
    plan = data.get("plan")
    price = data.get("price")

    if not tg_id or not plan or not price:
        return jsonify({"error": "missing params"}), 400

    inv_id = str(uuid.uuid4())
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO invoices (tg_id, plan, price, status) VALUES (%s, %s, %s, %s) RETURNING id",
        (tg_id, plan, price, "pending")
    )
    row_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": row_id, "invoice_uuid": inv_id, "plan": plan, "price": price})

# ✅ Verify Payment (placeholder)
@app.route("/api/verify_payment", methods=["POST"])
def verify_payment():
    data = request.get_json()
    tx = data.get("tx")
    invoice_id = data.get("invoice_id")

    if not tx or not invoice_id:
        return jsonify({"error": "missing tx or invoice"}), 400

    # TODO: Add real blockchain verification here
    # For now, mark invoice as paid
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE invoices SET status='paid' WHERE id=%s", (invoice_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"ok": True, "msg": "Payment marked as paid"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))