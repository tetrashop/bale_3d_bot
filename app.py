import os
import json
import uuid
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')

if not BOT_TOKEN or not PROVIDER_TOKEN:
    raise Exception("توکن‌ها در فایل .env تنظیم نشده‌اند")

# دیکشنری موقت برای نگهداری وضعیت پرداخت‌ها (در حافظه، در Vercel ممکن است ریست شود اما برای کار کافی است)
pending_payments = {}

def send_invoice(chat_id, payload, amount_rial=10000):
    """
    ارسال فاکتور به کاربر
    amount_rial: مبلغ به ریال (۱۰۰۰۰ ریال = ۱۰۰۰ تومان)
    """
    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendInvoice"
    data = {
        "chat_id": chat_id,
        "title": "تبدیل 2D به 3D",
        "description": "تبدیل عکس شما به مدل سه‌بعدی OBJ",
        "payload": payload,
        "provider_token": PROVIDER_TOKEN,
        "start_parameter": "convert_3d",
        "currency": "IRR",
        "prices": [{"label": "هزینه تبدیل", "amount": amount_rial}]
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        return resp.json()
    except Exception as e:
        print(f"خطا در ارسال فاکتور: {e}")
        return None

def convert_image_to_obj(image_bytes):
    """تبدیل تصویر به فایل OBJ (مدل برجستگی ساده)"""
    img = Image.open(BytesIO(image_bytes)).convert('L')
    img = img.resize((60, 60))
    pixels = np.array(img)
    obj_lines = ["# مدل سه‌بعدی ساخته شده از تصویر", "o Model"]
    verts = []
    scale_z = 0.04
    step = 0.1
    for y in range(pixels.shape[0]):
        for x in range(pixels.shape[1]):
            z = (255 - pixels[y, x]) / 255.0 * scale_z
            verts.append((x*step, y*step, z))
    for v in verts:
        obj_lines.append(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}")
    w = pixels.shape[1]
    for y in range(pixels.shape[0]-1):
        for x in range(w-1):
            i1 = y*w + x + 1
            i2 = y*w + (x+1) + 1
            i3 = (y+1)*w + (x+1) + 1
            i4 = (y+1)*w + x + 1
            obj_lines.append(f"f {i1} {i2} {i3} {i4}")
    return "\n".join(obj_lines)

# ---------- وب‌هوک ربات (دریافت پیام و پرداخت موفق) ----------
@app.route('/api/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return jsonify({"ok": False}), 400
    # پردازش پیام متنی
    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        if 'text' in msg and msg['text'] == '/start':
            # ارسال پیام خوش‌آمدگویی با راهنما
            url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, json={
                "chat_id": chat_id,
                "text": "سلام! به ربات تبدیل 2D به 3D خوش آمدید.\nبرای پرداخت و استفاده، به وب‌سایت زیر بروید:\nhttps://tetrashop-bale3dbot.vercel.app"
            })
        elif 'text' in msg and msg['text'].startswith('/start pay_'):
            # پرداخت از طریق لینک عمیق (اختیاری)
            payload = msg['text'].replace('/start pay_', '')
            send_invoice(chat_id, payload)
    # پرداخت موفق
    if 'successful_payment' in update.get('message', {}):
        sp = update['message']['successful_payment']
        payload = sp['payload']
        chat_id = update['message']['chat']['id']
        # بررسی وجود تصویر در حافظه موقت
        if payload in pending_payments:
            image_data = pending_payments[payload]['image']
            try:
                obj_content = convert_image_to_obj(image_data)
                obj_bytes = obj_content.encode('utf-8')
                # ارسال فایل OBJ به کاربر
                send_doc_url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendDocument"
                files = {'document': ('model.obj', obj_bytes, 'application/octet-stream')}
                data = {'chat_id': chat_id}
                requests.post(send_doc_url, files=files, data=data)
                # پاک کردن داده موقت
                del pending_payments[payload]
            except Exception as e:
                requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": f"خطا در تبدیل تصویر: {str(e)}"
                })
        else:
            requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "لطفاً ابتدا تصویر خود را در وب‌سایت آپلود کنید و سپس پرداخت را انجام دهید."
            })
    return jsonify({"ok": True}), 200

# ---------- اندپوینت وب‌سایت برای دریافت تصویر و ساخت فاکتور ----------
@app.route('/api/request_payment', methods=['POST'])
def request_payment():
    """دریافت تصویر و شناسه کاربر بله، سپس فاکتور ارسال می‌شود"""
    if 'image' not in request.files:
        return jsonify({"error": "تصویر ارسال نشده"}), 400
    chat_id = request.form.get('chat_id')
    if not chat_id:
        return jsonify({"error": "شناسه کاربر بله (chat_id) الزامی است"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "فایل خالی"}), 400
    # تولید payload یکتا
    payload = str(uuid.uuid4())
    # ذخیره موقت تصویر
    pending_payments[payload] = {'image': file.read(), 'chat_id': chat_id}
    # ارسال فاکتور به کاربر
    result = send_invoice(chat_id, payload, amount_rial=10000)
    if result and result.get('ok'):
        return jsonify({"status": "success", "message": "فاکتور به ربات ارسال شد. لطفاً در بله پرداخت را نهایی کنید."})
    else:
        # در صورت خطا، داده را پاک کن
        pending_payments.pop(payload, None)
        return jsonify({"error": "خطا در ارسال فاکتور", "details": result}), 500

# ---------- صفحه اصلی وب‌سایت (فرانت‌اند) ----------
@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
