from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

# Database file path
db_file = 'webhook_data.db'

# Ensure the templates folder exists
if not os.path.exists('templates'):
    os.makedirs('templates')

# Ensure dashboard.html exists in the templates folder
if not os.path.exists('templates/dashboard.html'):
    with open('templates/dashboard.html', 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard</title>
        </head>
        <body>
            <h1>Webhook Dashboard</h1>
            <table border="1">
                <tr>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                </tr>
                {% for row in rows %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[2] }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """)

# Initialize the database
def init_db():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS email_status (
                    email TEXT,
                    status TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

# Route for the webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if isinstance(data, list):
            responses = []
            for item in data:
                email = item.get('email', 'Unknown')
                status = item.get('status', 'Unknown')
                timestamp = item.get('timestamp', 'Unknown')
                save_to_db(email, status, timestamp)
                responses.append({'email': email, 'status': 'saved'})
            return jsonify(responses), 200
        else:
            email = data.get('email', 'Unknown')
            status = data.get('status', 'Unknown')
            timestamp = data.get('timestamp', 'Unknown')
            save_to_db(email, status, timestamp)
            return jsonify({'message': 'Data saved', 'email': email}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Route for the dashboard
@app.route('/')
def dashboard():
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT * FROM email_status')
    rows = c.fetchall()
    conn.close()
    return render_template('dashboard.html', rows=rows)

# Function to save data to the database
def save_to_db(email, status, timestamp):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('INSERT INTO email_status (email, status, timestamp) VALUES (?, ?, ?)', (email, status, timestamp))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
