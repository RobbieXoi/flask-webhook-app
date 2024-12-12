from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configure database
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///webhook_data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define database model
class EmailStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

# Create database tables (if they don't already exist)
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    """Dashboard route to display email statuses."""
    rows = EmailStatus.query.all()
    return render_template('dashboard.html', rows=rows)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint to receive and process data."""
    try:
        data = request.get_json()
        if isinstance(data, list):
            for entry in data:
                email = entry.get('email')
                status = entry.get('event')
                if email and status:
                    db.session.add(EmailStatus(email=email, status=status))
            db.session.commit()
        else:
            email = data.get('email')
            status = data.get('event')
            if email and status:
                db.session.add(EmailStatus(email=email, status=status))
                db.session.commit()
        return jsonify({"message": "Data received and processed."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
