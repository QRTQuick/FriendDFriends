from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = "chat_messages.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            text TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Root route
@app.route("/")
def home():
    return jsonify({"status": "FriendDFriends API is running"}), 200

# Send message
@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    sender = data.get("sender")
    receiver = data.get("receiver")
    text = data.get("text")

    if not sender or not receiver or not text:
        return jsonify({"error": "Missing fields"}), 400

    timestamp = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (sender, receiver, text, timestamp) VALUES (?, ?, ?, ?)",
        (sender, receiver, text, timestamp)
    )
    msg_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "id": msg_id,
        "sender": sender,
        "receiver": receiver,
        "text": text,
        "timestamp": timestamp
    }), 200

# Fetch all messages for a user
@app.route("/messages/<username>", methods=["GET"])
def get_messages(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT id, sender, receiver, text, timestamp FROM messages WHERE receiver=? OR sender=? ORDER BY id ASC",
        (username, username)
    )
    rows = c.fetchall()
    conn.close()

    messages = []
    for r in rows:
        messages.append({
            "id": r[0],
            "sender": r[1],
            "receiver": r[2],
            "text": r[3],
            "timestamp": r[4]
        })

    return jsonify(messages), 200

if __name__ == "__main__":
    app.run(debug=True)