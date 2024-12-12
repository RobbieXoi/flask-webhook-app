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
    event_type = db.Column(db.String(50))  # Loại sự kiện
    campaign = db.Column(db.String(100))  # Chiến dịch

# Create database tables (if they don't already exist)
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    """Dashboard route to display email statuses and statistics."""
    rows = EmailStatus.query.all()

    # Thống kê tổng quan
    total_emails = EmailStatus.query.count()
    sent_count = EmailStatus.query.filter_by(status='Sent').count()
    opened_count = EmailStatus.query.filter_by(status='Opened').count()
    failed_count = EmailStatus.query.filter_by(status='Failed').count()
    click_count = EmailStatus.query.filter_by(status='Clicked').count()

    open_rate = (opened_count / total_emails) * 100 if total_emails > 0 else 0
    error_rate = (failed_count / total_emails) * 100 if total_emails > 0 else 0
    click_rate = (click_count / total_emails) * 100 if total_emails > 0 else 0

    stats = {
        'total_emails': total_emails,
        'sent_count': sent_count,
        'opened_count': opened_count,
        'failed_count': failed_count,
        'click_count': click_count,
        'open_rate': open_rate,
        'error_rate': error_rate,
        'click_rate': click_rate,
    }
    return render_template('dashboard.html', rows=rows, stats=stats)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint to receive and process data."""
    try:
        data = request.get_json()
        if isinstance(data, list):
            for entry in data:
                email = entry.get('email')
                status = entry.get('event')
                event_type = entry.get('type')  # Loại sự kiện
                campaign = entry.get('campaign')  # Chiến dịch
                if email and status:
                    db.session.add(EmailStatus(
                        email=email, status=status,
                        event_type=event_type, campaign=campaign
                    ))
            db.session.commit()
        else:
            email = data.get('email')
            status = data.get('event')
            event_type = data.get('type')  # Loại sự kiện
            campaign = data.get('campaign')  # Chiến dịch
            if email and status:
                db.session.add(EmailStatus(
                    email=email, status=status,
                    event_type=event_type, campaign=campaign
                ))
                db.session.commit()
        return jsonify({"message": "Data received and processed."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
