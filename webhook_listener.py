from flask import Flask, request, jsonify
import requests
import logging
import json
import os

app = Flask(__name__)

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='webhook.log'  # Log to file in production
)
logger = logging.getLogger(__name__)

# BTCPay Server API Configuration
BTCPAY_URL = os.getenv('BTCPAY_URL', "https://bti.btcpayprovider.com")
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', "333")

# Add a root route to confirm the server is running
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "endpoints": {
            "webhook": "/btcpay-webhook (POST)"
        }
    })

@app.route('/btcpay-webhook', methods=['POST'])
def btcpay_webhook():
    try:
        # Log the raw request data
        logger.info("Received webhook request")
        logger.info(f"Headers: {dict(request.headers)}")
        
        data = request.json
        logger.info(f"Webhook payload: {json.dumps(data, indent=2)}")
        
        # Extract invoice details from the new payload structure
        webhook_type = data.get("type")
        user_email = data.get("metadata", {}).get("buyerEmail")
        
        logger.info(f"Webhook type: {webhook_type}, User email: {user_email}")

        # Check if this is a payment settlement webhook and we have an email
        if webhook_type == "InvoicePaymentSettled" and user_email:
            logger.info(f"Creating new user for {user_email}")
            
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

            logger.info(f"BTCPay API response status: {response.status_code}")
            logger.info(f"BTCPay API response: {response.text}")

            # Check for both 200 and 201 status codes
            if response.status_code in [200, 201]:
                return jsonify({
                    "message": "User created successfully",
                    "user_id": response.json().get("id")
                }), 200
            else:
                return jsonify({"error": "Failed to create user", "details": response.text}), 400

        return jsonify({"message": "Webhook received"}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# Add error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not found",
        "message": "The requested URL was not found on the server.",
        "available_endpoints": {
            "root": "/ (GET)",
            "webhook": "/btcpay-webhook (POST)"
        }
    }), 404

if __name__ == '__main__':
    # Use production server instead of Flask's development server
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
