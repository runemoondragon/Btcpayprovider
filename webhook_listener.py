from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# BTCPay Server API Configuration
BTCPAY_URL = "https://bti.btcpayprovider.com"
ADMIN_API_KEY = "58e1558dc63317d1b4bce39dc1295d0c6eafab01"

@app.route('/btcpay-webhook', methods=['POST'])
def btcpay_webhook():
    data = request.json  # Get webhook payload
    
    # Extract invoice details
    invoice_status = data.get("Invoice", {}).get("Status")
    user_email = data.get("Invoice", {}).get("buyer", {}).get("email")

    if invoice_status == "complete" and user_email:
        print(f"Creating new user for {user_email}")
        
        # Create user on BTCPay
        user_payload = {
            "email": user_email,
            "name": user_email
        }

        headers = {
            "Authorization": f"token {ADMIN_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{BTCPAY_URL}/api/v1/users",
            json=user_payload,
            headers=headers
        )

        if response.status_code == 200:
            return jsonify({"message": "User created successfully"}), 200
        else:
            return jsonify({"error": "Failed to create user", "details": response.text}), 400

    return jsonify({"message": "Webhook received"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
