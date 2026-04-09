import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Masked Environment Variable (Set this in Vercel dashboard)
# WEBHOOK_URL: Your app's ais-pre URL + /api/webhook/tradingview/YOUR_SECRET
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST', 'GET'])
def proxy(path):
    if not WEBHOOK_URL:
        return jsonify({"status": "error", "message": "WEBHOOK_URL environment variable not set in Vercel"}), 500

    if request.method == 'GET':
        return jsonify({
            "status": "proxy_active",
            "message": "Vercel Proxy is running. Send POST requests here.",
            "target_configured": bool(WEBHOOK_URL)
        })

    try:
        # Get data from TradingView
        data = request.get_json(silent=True) or request.get_data(as_text=True)
        
        # Forward to the main app
        headers = {'Content-Type': 'application/json'}
        # We use the WEBHOOK_URL directly as the target
        response = requests.post(WEBHOOK_URL, json=data if isinstance(data, dict) else {"raw": data}, headers=headers, timeout=10)
        
        return jsonify({
            "status": "forwarded",
            "upstream_status": response.status_code,
            "upstream_response": response.text
        }), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel requires the app object to be named 'app'
if __name__ == '__main__':
    app.run()
