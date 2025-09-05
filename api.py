from flask import Flask, request, jsonify
import psycopg2, os

app = Flask(__name__)
DB_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DB_URL)

@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    data = request.json
    invoice_id = data.get("invoice_id")
    if not invoice_id:
        return jsonify({"error": "No invoice_id"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE invoices SET paid=TRUE WHERE id=%s", (invoice_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"})