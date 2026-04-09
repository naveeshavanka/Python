import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Masked Environment Variable (Set this in Vercel dashboard)
# WEBHOOK_URL: Your app's ais-pre URL + /api/webhook/tradingview/YOUR_SECRET
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def proxy(path):
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204

    if not WEBHOOK_URL:
        return jsonify({"status": "error", "message": "WEBHOOK_URL environment variable not set in Vercel"}), 500

    if request.method == 'GET':
        return jsonify({
            "status": "proxy_active",
            "message": "Vercel Proxy is running. Send POST requests here.",
            "target_configured": bool(WEBHOOK_URL),
            "path_received": path
        })

    try:
        # Get data from TradingView
        # TradingView usually sends JSON, but sometimes plain text
        if request.is_json:
            data = request.get_json()
        else:
            data = request.get_data(as_text=True)
        
        # Forward to the main app
        headers = {'Content-Type': 'application/json'}
        
        # If data is already a dict, send as JSON. If string, wrap it.
        json_payload = data if isinstance(data, dict) else {"raw": data}
        
        response = requests.post(WEBHOOK_URL, json=json_payload, headers=headers, timeout=15)
        
        # Always return 200 OK to TradingView to acknowledge receipt, 
        # even if the upstream app had a validation error.
        return jsonify({
            "status": "received",
            "upstream_status": response.status_code,
            "upstream_response": response.text
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel requires the app object to be named 'app'
if __name__ == '__main__':
    app.run()
