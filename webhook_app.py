from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        # Handle POST request (SendGrid gửi webhook)
        data = request.json
        # Thực hiện xử lý dữ liệu
        return jsonify({'status': 'success', 'message': 'Webhook received'}), 200
    elif request.method == 'GET':
        # Handle GET request (kiểm tra hoặc debug)
        return jsonify({'status': 'running', 'message': 'Webhook is ready'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
