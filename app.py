from flask import Flask, request, jsonify, send_file
import requests
import os
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("WARNING: BOT_TOKEN not set")

# ---------- ربات بله (وب‌هوک) ----------
@app.route('/api/webhook', methods=['POST'])
def webhook():
    if not BOT_TOKEN:
        return jsonify({"error": "BOT_TOKEN not set"}), 500
    update = request.get_json()
    if not update or 'message' not in update:
        return jsonify({"ok": True}), 200
    msg = update['message']
    chat_id = msg['chat']['id']
    if 'text' in msg and msg['text'] == '/start':
        url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": "سلام! به ربات تبدیل 2D به 3D خوش آمدید.\nلطفاً از وب‌سایت ما استفاده کنید:\nhttps://tetrashop-bale3dbot.vercel.app"}
        requests.post(url, json=payload)
    elif 'photo' in msg:
        # می‌توانیم عکس را پردازش کنیم (اختیاری)
        url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": "لطفاً از وب‌سایت برای تبدیل استفاده کنید."}
        requests.post(url, json=payload)
    return jsonify({"ok": True}), 200

# ---------- تبدیل 2D به 3D (اندپوینت برای وب‌سایت) ----------
@app.route('/api/convert', methods=['POST'])
def convert():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    try:
        # باز کردن و تبدیل تصویر
        img = Image.open(file.stream).convert('L')
        img = img.resize((80, 80))  # ابعاد مناسب
        pixels = np.array(img)
        
        obj_lines = []
        obj_lines.append("# 2D to 3D conversion")
        obj_lines.append("o Model")
        # رأس‌ها
        verts = []
        h_scale = 0.03
        step = 0.08
        for y in range(pixels.shape[0]):
            for x in range(pixels.shape[1]):
                z = pixels[y, x] / 255.0 * h_scale
                verts.append((x * step, y * step, z))
        for v in verts:
            obj_lines.append(f"v {v[0]} {v[1]} {v[2]}")
        # وجوه (مربع‌ها)
        width = pixels.shape[1]
        for y in range(pixels.shape[0]-1):
            for x in range(width-1):
                i1 = y*width + x + 1
                i2 = y*width + (x+1) + 1
                i3 = (y+1)*width + (x+1) + 1
                i4 = (y+1)*width + x + 1
                obj_lines.append(f"f {i1} {i2} {i3} {i4}")
        obj_data = "\n".join(obj_lines)
        obj_bytes = obj_data.encode('utf-8')
        return send_file(
            io.BytesIO(obj_bytes),
            mimetype='model/obj',
            as_attachment=True,
            download_name='model.obj'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# برای اجرای محلی (در Vercel به کار نمی‌آید، اما لازم است)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
