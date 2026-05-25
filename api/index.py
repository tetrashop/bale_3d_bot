from flask import Flask, request, jsonify
import requests
import os
import sys
import traceback

app = Flask(__name__)

# دریافت توکن از متغیرهای محیطی Vercel
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN environment variable is not set!")
else:
    print(f"BOT_TOKEN loaded successfully (first 10 chars: {BOT_TOKEN[:10]}...)")

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        # 1. بررسی اعتبار توکن
        if not BOT_TOKEN:
            print("ERROR: BOT_TOKEN is missing")
            return jsonify({"error": "BOT_TOKEN not set"}), 500

        # 2. دریافت اطلاعات از درخواست Bale
        update = request.get_json()
        if not update:
            print("ERROR: Invalid JSON received")
            return jsonify({"error": "Invalid JSON"}), 400

        print(f"Update received: {update}")

        # 3. پردازش پیام
        if 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']
            
            # 4. پاسخ به دستور /start
            if 'text' in msg and msg['text'] == '/start':
                send_url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": "سلام! ربات با موفقیت روی Vercel فعال شد."
                }
                response = requests.post(send_url, json=payload, timeout=10)
                print(f"Message sent to {chat_id}, response: {response.status_code}")
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        # چاپ خطا در لاگ‌های Vercel برای دیباگ
        print(f"EXCEPTION: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500
