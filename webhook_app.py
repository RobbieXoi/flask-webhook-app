from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('email_status.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS email_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

init_db()

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    email = data.get('email')
    status = data.get('status')

    if not email or not status:
        return jsonify({"error": "Missing email or status"}), 400

    # Save to database
    conn = sqlite3.connect('email_status.db')
    c = conn.cursor()
    c.execute("INSERT INTO email_status (email, status) VALUES (?, ?)", (email, status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Data received and stored", "email": email, "status": status}), 200

# Dashboard route
@app.route('/')
def dashboard():
    conn = sqlite3.connect('email_status.db')
    c = conn.cursor()
    c.execute("SELECT email, status, timestamp FROM email_status ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    return render_template('dashboard.html', rows=rows)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
