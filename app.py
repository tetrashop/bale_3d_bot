from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if not BOT_TOKEN:
        return jsonify({"error": "BOT_TOKEN not set"}), 500

    update = request.json
    print("Received update:", update)

    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        if 'text' in msg and msg['text'] == '/start':
            url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": "سلام! ربات فعال است."}
            try:
                requests.post(url, json=payload)
            except Exception as e:
                print(e)

    return jsonify({"status": "ok"}), 200
