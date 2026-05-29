import os
import uuid
import requests
from io import BytesIO
from flask import Flask, request, jsonify
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')

pending_payments = {}

# ---------- صفحه اصلی HTML ----------
@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>تبدیل 2D به 3D با ولت بله</title>
<style>
*{box-sizing:border-box;font-family:Tahoma,sans-serif}
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;justify-content:center;align-items:center;margin:0;padding:20px}
.card{background:white;border-radius:30px;padding:30px;max-width:600px;width:100%;box-shadow:0 25px 45px rgba(0,0,0,0.2);text-align:center}
h1{color:#333}
.upload-area{border:2px dashed #764ba2;border-radius:20px;padding:30px;cursor:pointer;background:#f9f9ff;margin-bottom:20px}
.upload-area:hover{background:#f0eaff}
#preview{max-width:100%;max-height:200px;display:none;margin:15px 0}
input{width:100%;padding:12px;margin:10px 0;border:1px solid #ddd;border-radius:25px;text-align:center}
button{background:linear-gradient(95deg,#667eea,#764ba2);border:none;color:white;padding:12px 25px;border-radius:40px;cursor:pointer;width:80%;font-weight:bold}
button:disabled{opacity:0.6}
.status{margin-top:15px;font-size:14px;color:#555}
.loading{display:none;margin:20px}
</style>
</head>
<body>
<div class="card"><h1>🖼️ تبدیل 2D به 3D</h1><p>عکس خود را آپلود کنید و شناسه کاربری بله را وارد کنید.</p>
<div class="upload-area" id="uploadArea">📸 کلیک یا بکشید<input type="file" id="fileInput" accept="image/*" style="display:none"><img id="preview"></div>
<input type="text" id="chatId" placeholder="شناسه کاربری بله (مثال: 431413093)" dir="ltr">
<button id="payBtn" disabled>💳 پرداخت با ولت بله (۱۰,۰۰۰ ریال)</button>
<div class="loading" id="loading">⏳ در حال ارسال...</div><div class="status" id="status"></div></div>
<script>
const up=document.getElementById('uploadArea'),fileInput=document.getElementById('fileInput'),preview=document.getElementById('preview'),chatId=document.getElementById('chatId'),payBtn=document.getElementById('payBtn'),loadingDiv=document.getElementById('loading'),statusDiv=document.getElementById('status');
let selectedFile=null;
up.onclick=()=>fileInput.click();
up.ondragover=e=>{e.preventDefault();up.style.background='#e0d6ff';};
up.ondragleave=e=>{up.style.background='#f9f9ff';};
up.ondrop=e=>{e.preventDefault();up.style.background='#f9f9ff';const f=e.dataTransfer.files[0];if(f&&f.type.startsWith('image/')) handleFile(f);else statusDiv.innerText='❌ فقط تصویر مجاز است';};
fileInput.onchange=e=>{if(e.target.files[0]) handleFile(e.target.files[0]);};
function handleFile(f){selectedFile=f;const reader=new FileReader();reader.onload=e=>{preview.src=e.target.result;preview.style.display='block';};reader.readAsDataURL(f);payBtn.disabled=false;statusDiv.innerText='✅ عکس انتخاب شد. شناسه خود را وارد کنید.';}
payBtn.onclick=async()=>{if(!selectedFile)return;const cid=chatId.value.trim();if(!cid){statusDiv.innerText='❌ شناسه کاربری را وارد کنید';return;}payBtn.disabled=true;loadingDiv.style.display='block';statusDiv.innerText='در حال ارسال...';const fd=new FormData();fd.append('image',selectedFile);fd.append('chat_id',cid);try{const res=await fetch('/api/request_payment',{method:'POST',body:fd});const data=await res.json();if(res.ok&&data.status==='success'){statusDiv.innerHTML='✅ فاکتور به ربات ارسال شد. لطفاً در بله پرداخت را نهایی کنید.<br>پس از پرداخت، مدل سه‌بعدی ارسال می‌شود.';}else{statusDiv.innerText='❌ خطا: '+(data.error||'مشخص نیست');}}catch(err){statusDiv.innerText='❌ خطای شبکه: '+err.message;}finally{loadingDiv.style.display='none';payBtn.disabled=false;}};
</script>
</body></html>'''

# ---------- توابع کمکی ----------
def send_invoice(chat_id, payload, amount_rial=10000):
    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendInvoice"
    data = {
        "chat_id": chat_id,
        "title": "تبدیل 2D به 3D",
        "description": "تبدیل عکس شما به مدل OBJ",
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
        print(f"Invoice error: {e}")
        return None

def convert_image_to_obj(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert('L')
    img = img.resize((60, 60))
    width, height = img.size
    pixels = list(img.getdata())
    matrix = [pixels[i*width:(i+1)*width] for i in range(height)]
    obj_lines = ["# 2D to 3D model", "o Model"]
    verts = []
    scale_z = 0.04
    step = 0.1
    for y in range(height):
        for x in range(width):
            z = (255 - matrix[y][x]) / 255.0 * scale_z
            verts.append((x*step, y*step, z))
    for v in verts:
        obj_lines.append(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}")
    for y in range(height-1):
        for x in range(width-1):
            i1 = y*width + x + 1
            i2 = y*width + (x+1) + 1
            i3 = (y+1)*width + (x+1) + 1
            i4 = (y+1)*width + x + 1
            obj_lines.append(f"f {i1} {i2} {i3} {i4}")
    return "\n".join(obj_lines)

# ---------- وب‌هوک ----------
@app.route('/api/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update:
        return jsonify({"ok": False}), 400
    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        if msg.get('text') == '/start':
            requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "سلام! از وب‌سایت استفاده کنید:\nhttps://tetrashop-bale3dbot.vercel.app"
            })
    if 'successful_payment' in update.get('message', {}):
        sp = update['message']['successful_payment']
        payload = sp['payload']
        chat_id = update['message']['chat']['id']
        if payload in pending_payments:
            img_data = pending_payments[payload]['image']
            try:
                obj_str = convert_image_to_obj(img_data)
                obj_bytes = obj_str.encode('utf-8')
                files = {'document': ('model.obj', obj_bytes, 'application/octet-stream')}
                data = {'chat_id': chat_id}
                requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendDocument", files=files, data=data)
                del pending_payments[payload]
            except Exception as e:
                requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": f"خطا در ساخت مدل: {str(e)}"
                })
        else:
            requests.post(f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "لطفاً ابتدا تصویر را در وب‌سایت آپلود کنید."
            })
    return jsonify({"ok": True}), 200

# ---------- درخواست پرداخت ----------
@app.route('/api/request_payment', methods=['POST'])
def request_payment():
    if 'image' not in request.files:
        return jsonify({"error": "تصویر ارسال نشده"}), 400
    chat_id = request.form.get('chat_id')
    if not chat_id:
        return jsonify({"error": "شناسه کاربر الزامی است"}), 400
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

# برای Vercel، اپلیکیشن Flask را به عنوان `app` صادر می‌کنیم
app = app
