from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

app = Flask(__name__)
CORS(app)

# PostgreSQL credentials
import os

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ["DB_NAME"]
def create_database():
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database '{DB_NAME}' created.")
    else:
        print(f"Database '{DB_NAME}' already exists.")
    cur.close()
    conn.close()

# Step 2: Create messages table
def init_db():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    c.close()
    conn.close()

create_database()
init_db()

# --- Flask Routes ---
@app.route("/")
def home():
    return jsonify({"status": "FriendDFriends API is running"}), 200

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    sender = data.get("sender")
    receiver = data.get("receiver")
    text = data.get("text")

    if not sender or not receiver or not text:
        return jsonify({"error": "Missing fields"}), 400

    timestamp = datetime.now().strftime("%H:%M:%S")

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (sender, receiver, text, timestamp) VALUES (%s, %s, %s, %s) RETURNING id",
        (sender, receiver, text, timestamp)
    )
    msg_id = c.fetchone()[0]
    conn.commit()
    c.close()
    conn.close()

    return jsonify({"id": msg_id, "sender": sender, "receiver": receiver, "text": text, "timestamp": timestamp}), 200

@app.route("/messages/<username>", methods=["GET"])
def get_messages(username):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    c = conn.cursor()
    c.execute(
        "SELECT id, sender, receiver, text, timestamp FROM messages WHERE receiver=%s OR sender=%s ORDER BY id ASC",
        (username, username)
    )
    rows = c.fetchall()
    c.close()
    conn.close()

    return jsonify([{"id": r[0], "sender": r[1], "receiver": r[2], "text": r[3], "timestamp": r[4]} for r in rows]), 200

if __name__ == "__main__":
    app.run(debug=True)