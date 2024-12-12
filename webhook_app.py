from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import logging

app = Flask(__name__)

# Cấu hình database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mô hình Email
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Mô hình Webhook Log
class WebhookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Tạo database
with app.app_context():
    db.create_all()

# Hàm xác thực từng sự kiện
def validate_event(event):
    required_fields = ["email", "event"]
    return all(field in event for field in required_fields)

# Endpoint webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Kiểm tra định dạng JSON
        if not request.is_json:
            return jsonify({"error": "Invalid JSON format"}), 400

        data = request.get_json()

        # Kiểm tra dữ liệu là danh sách
        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of events"}), 400

        # Xử lý từng sự kiện
        for event in data:
            if validate_event(event):
                email = event.get("email")
                event_type = event.get("event")

                # Lưu log webhook
                webhook_log = WebhookLog(
                    event_type=event_type, payload=str(event)
                )
                db.session.add(webhook_log)

                # Cập nhật trạng thái email
                email_record = Email.query.filter_by(email=email).first()
                if email_record:
                    email_record.status = event_type
                    email_record.timestamp = datetime.datetime.utcnow()
                else:
                    # Tạo bản ghi mới nếu không tìm thấy email
                    email_record = Email(
                        email=email, status=event_type, timestamp=datetime.datetime.utcnow()
                    )
                    db.session.add(email_record)

        # Lưu thay đổi
        db.session.commit()

        return jsonify({"message": "Webhook processed successfully"}), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
