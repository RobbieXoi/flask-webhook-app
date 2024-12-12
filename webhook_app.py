from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# Cấu hình database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Email
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Model Webhook Logs
class WebhookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Tạo bảng trong database
@app.before_first_request
def create_tables():
    db.create_all()

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if isinstance(data, dict):  # Kiểm tra dữ liệu có đúng định dạng JSON object
        event_type = data.get('event')
        email = data.get('email')
        subject = data.get('subject', 'N/A')

        # Lưu webhook log
        webhook_log = WebhookLog(event_type=event_type, payload=str(data))
        db.session.add(webhook_log)

        # Cập nhật trạng thái email
        email_record = Email.query.filter_by(email=email).first()
        if email_record:
            email_record.status = event_type
            email_record.timestamp = datetime.datetime.utcnow()
        else:
            # Thêm mới nếu không tìm thấy
            email_record = Email(email=email, subject=subject, status=event_type)
            db.session.add(email_record)

        db.session.commit()
        return jsonify({"message": "Webhook processed"}), 200
    else:
        return jsonify({"error": "Invalid data format"}), 400

# Dashboard endpoint
@app.route('/')
def dashboard():
    emails = Email.query.order_by(Email.timestamp.desc()).all()
    webhook_logs = WebhookLog.query.order_by(WebhookLog.timestamp.desc()).limit(10).all()

    # Thống kê
    stats = {
        "total_sent": Email.query.filter(Email.status == "sent").count(),
        "total_opens": Email.query.filter(Email.status == "opened").count(),
        "total_clicks": Email.query.filter(Email.status == "clicked").count(),
        "bounce_rate": round(
            100 * Email.query.filter(Email.status == "bounced").count() / max(1, Email.query.count()), 2
        ),
        "pending": Email.query.filter(Email.status == "pending").count(),
    }

    return render_template("dashboard.html", emails=emails, webhook_logs=webhook_logs, stats=stats)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
