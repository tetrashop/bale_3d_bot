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
    print("ERROR: Tokens not set in environment")

pending_payments = {}

# ---------- صفحه اصلی (HTML توکار) ----------
@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تبدیل 2D به 3D با ولت بله</title>
    <style>
        * { box-sizing: border-box; font-family: Tahoma, sans-serif; }
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; margin: 0; padding: 20px; }
        .card { background: white; border-radius: 30px; padding: 30px; max-width: 600px; width: 100%; box-shadow: 0 25px 45px rgba(0,0,0,0.2); text-align: center; }
        h1 { color: #333; margin-bottom: 10px; }
        p { color: #666; margin-bottom: 20px; }
        .upload-area { border: 2px dashed #764ba2; border-radius: 20px; padding: 30px; cursor: pointer; transition: 0.3s; background: #f9f9ff; margin-bottom: 20px; }
        .upload-area:hover { background: #f0eaff; }
        #preview { max-width: 100%; max-height: 200px; margin: 15px 0; display: none; border-radius: 15px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 25px; font-size: 16px; text-align: center; direction: ltr; }
        button { background: linear-gradient(95deg, #667eea, #764ba2); border: none; color: white; padding: 12px 25px; border-radius: 40px; font-size: 16px; cursor: pointer; margin: 10px; font-weight: bold; width: 80%; }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .status { margin-top: 15px; font-size: 14px; color: #555; }
        .loading { display: none; margin: 20px; }
    </style>
</head>
<body>
<div class="card">
    <h1>🖼️ تبدیل 2D به 3D</h1>
    <p>عکس خود را آپلود کنید، سپس شناسه کاربری بله خود را وارد کرده و پرداخت را انجام دهید.</p>
    <div class="upload-area" id="uploadArea">
        📸 کلیک کنید یا عکس را بکشید و رها کنید
        <input type="file" id="fileInput" accept="image/*" style="display: none;">
        <img id="preview">
    </div>
    <input type="text" id="chatId" placeholder="شناسه کاربری بله (مثال: 431413093)" dir="ltr">
    <button id="payBtn" disabled>💳 پرداخت با ولت بله (۱۰,۰۰۰ ریال)</button>
    <div class="loading" id="loading">⏳ در حال ارسال درخواست به ربات...</div>
    <div class="status" id="status"></div>
    <p style="font-size:12px; margin-top:20px;">پس از پرداخت، مدل سه‌بعدی در همین ربات برای شما ارسال می‌شود.</p>
</div>
<script>
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const chatIdInput = document.getElementById('chatId');
    const payBtn = document.getElementById('payBtn');
    const loadingDiv = document.getElementById('loading');
    const statusDiv = document.getElementById('status');
    let selectedFile = null;

    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.style.background = '#e0d6ff'; });
    uploadArea.addEventListener('dragleave', () => { uploadArea.style.background = '#f9f9ff'; });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#f9f9ff';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) handleFile(file);
        else statusDiv.innerText = '❌ فقط فایل تصویری مجاز است';
    });
    fileInput.addEventListener('change', (e) => { if(e.target.files[0]) handleFile(e.target.files[0]); });

    function handleFile(file) {
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
        payBtn.disabled = false;
        statusDiv.innerText = '✅ عکس انتخاب شد. لطفاً شناسه کاربری خود را وارد کنید.';
    }

    payBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        const chatId = chatIdInput.value.trim();
        if (!chatId) {
            statusDiv.innerText = '❌ لطفاً شناسه کاربری بله خود را وارد کنید.';
            return;
        }
        payBtn.disabled = true;
        loadingDiv.style.display = 'block';
        statusDiv.innerText = 'در حال ارسال به سرور...';
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('chat_id', chatId);
        try {
            const response = await fetch('/api/request_payment', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (response.ok && result.status === 'success') {
                statusDiv.innerHTML = '✅ فاکتور به ربات شما ارسال شد. لطفاً اکنون در پیام‌رسان بله، روی دکمه پرداخت کلیک کنید و هزینه را پرداخت نمایید.<br>پس از پرداخت، مدل سه‌بعدی برای شما ارسال خواهد شد.';
            } else {
                statusDiv.innerText = '❌ خطا: ' + (result.error || 'مشخص نیست');
            }
        } catch (err) {
            statusDiv.innerText = '❌ خطای شبکه: ' + err.message;
        } finally {
            loadingDiv.style.display = 'none';
            payBtn.disabled = false;
        }
    });
</script>
</body>
</html>
    '''

# ---------- توابع کمکی ----------
def send_invoice(chat_id, payload, amount_rial=10000):
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
        print(f"Error sending invoice: {e}")
        return None

def convert_image_to_obj(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert('L')
    img = img.resize((60, 60))
    pixels = np.array(img)
    obj_lines = ["# 2D to 3D model", "o Model"]
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

# ---------- وب‌هوک ربات ----------
@app.route('/api/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return jsonify({"ok": False}), 400
    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        if 'text' in msg and msg['text'] == '/start':
            requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "سلام! به ربات تبدیل 2D به 3D خوش آمدید.\nلطفاً از وب‌سایت زیر استفاده کنید:\nhttps://tetrashop-bale3dbot.vercel.app"
            })
    if 'successful_payment' in update.get('message', {}):
        sp = update['message']['successful_payment']
        payload = sp['payload']
        chat_id = update['message']['chat']['id']
        if payload in pending_payments:
            image_data = pending_payments[payload]['image']
            try:
                obj_content = convert_image_to_obj(image_data)
                obj_bytes = obj_content.encode('utf-8')
                files = {'document': ('model.obj', obj_bytes, 'application/octet-stream')}
                data = {'chat_id': chat_id}
                requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendDocument", files=files, data=data)
                del pending_payments[payload]
            except Exception as e:
                requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": f"خطا در تبدیل: {str(e)}"
                })
        else:
            requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "لطفاً ابتدا تصویر خود را در وب‌سایت آپلود کنید."
            })
    return jsonify({"ok": True}), 200

# ---------- درخواست پرداخت از وب‌سایت ----------
@app.route('/api/request_payment', methods=['POST'])
def request_payment():
    if 'image' not in request.files:
        return jsonify({"error": "تصویر ارسال نشده"}), 400
    chat_id = request.form.get('chat_id')
    if not chat_id:
        return jsonify({"error": "شناسه کاربر بله الزامی است"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "فایل خالی"}), 400
    payload = str(uuid.uuid4())
    pending_payments[payload] = {'image': file.read(), 'chat_id': chat_id}
    result = send_invoice(chat_id, payload, amount_rial=10000)
    if result and result.get('ok'):
        return jsonify({"status": "success", "message": "فاکتور ارسال شد"})
    else:
        pending_payments.pop(payload, None)
        return jsonify({"error": "خطا در ارسال فاکتور", "details": result}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
