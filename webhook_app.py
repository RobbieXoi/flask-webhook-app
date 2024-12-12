from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# Cấu hình database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Định nghĩa model Email
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Khởi tạo database
with app.app_context():
    db.create_all()

@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.get_json()
    for event in data:
        email = event.get("email")
        status = event.get("event")

        if email and status:
            email_record = Email.query.filter_by(email=email).first()
            if email_record:
                email_record.status = status
                email_record.timestamp = datetime.datetime.utcnow()
            else:
                new_email = Email(email=email, status=status)
                db.session.add(new_email)

    db.session.commit()
    return jsonify({"message": "Webhook processed"}), 200

if __name__ == "__main__":
    app.run(debug=True)
