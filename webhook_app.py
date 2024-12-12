from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Webhook is running!"  # Trả về thông báo khi truy cập URL gốc

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        data = request.json  # Lấy dữ liệu JSON từ request
        # Xử lý dữ liệu webhook
        print(f"Received webhook data: {data}")
        return jsonify({"status": "success", "message": "Webhook received"}), 200
    return jsonify({"status": "failure", "message": "Invalid method"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
