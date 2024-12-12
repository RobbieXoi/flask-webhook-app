from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime

app = Flask(__name__)

# Cấu hình database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model Email
class Email(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(120), nullable=False)
    subject = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Model Webhook Logs
class WebhookLog(db.Model):
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Khởi tạo database khi ứng dụng chạy
with app.app_context():
    db.create_all()

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Lấy dữ liệu JSON từ request
        data = request.get_json()
        
        # Ghi log dữ liệu nhận được
        print(f"Received POST data: {data}")

        # Kiểm tra dữ liệu JSON hợp lệ
        if not data or not isinstance(data, dict):
            print("Invalid JSON data")
            return jsonify({"error": "Invalid JSON format"}), 400

        # Kiểm tra các trường cần thiết
        event_type = data.get('event')
        email = data.get('email')

        if not event_type or not email:
            print("Missing required fields: 'event' or 'email'")
            return jsonify({"error": "Missing required fields (event, email)"}), 400

        # Ghi nhận sự kiện vào database
        subject = data.get('subject', 'N/A')  # Giá trị mặc định nếu không có 'subject'
        webhook_log = WebhookLog(event_type=event_type, payload=str(data))
        db.session.add(webhook_log)

        # Cập nhật trạng thái email
        email_record = Email.query.filter_by(email=email).first()
        if email_record:
            email_record.status = event_type
            email_record.timestamp = datetime.datetime.utcnow()
        else:
            # Tạo bản ghi mới nếu không tìm thấy email
            email_record = Email(email=email, subject=subject, status=event_type)
            db.session.add(email_record)

        db.session.commit()
        print("Webhook processed successfully")
        return jsonify({"message": "Webhook processed successfully"}), 200
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

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
