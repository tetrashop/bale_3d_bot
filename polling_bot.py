import os
import time
import requests
import subprocess
from pathlib import Path

BOT_TOKEN = "659328109:t9eYCoTwNUbuGhRaovXtN95IJjaYIiJpBRo"
BASE_URL = f"https://api.bale.ai/bot{BOT_TOKEN}"
last_update_id = 0

def send_message(chat_id, text):
    try:
        requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": text})
    except Exception as e:
        print("send_message error:", e)

def send_document(chat_id, file_path):
    try:
        with open(file_path, 'rb') as f:
            requests.post(f"{BASE_URL}/sendDocument", data={"chat_id": chat_id}, files={"document": f})
    except Exception as e:
        print("send_document error:", e)

def process_photo(chat_id, file_id):
    try:
        # دریافت اطلاعات فایل
        r = requests.get(f"{BASE_URL}/getFile", params={"file_id": file_id})
        file_info = r.json()
        if not file_info.get("ok"):
            send_message(chat_id, "خطا در دریافت تصویر")
            return
        file_path = file_info["result"]["file_path"]
        dl_url = f"https://api.bale.ai/file/bot{BOT_TOKEN}/{file_path}"
        img_data = requests.get(dl_url).content
        temp_img = f"/tmp/{chat_id}_input.jpg"
        with open(temp_img, "wb") as f:
            f.write(img_data)
        output_obj = f"/tmp/{chat_id}_model.obj"
        # اجرای موتور تبدیل
        result = subprocess.run(
            ["python3", "engine_3d.py", temp_img, output_obj],
            capture_output=True, text=True
        )
        if result.returncode == 0 and Path(output_obj).exists():
            send_document(chat_id, output_obj)
            send_message(chat_id, "✅ مدل سه‌بعدی شما آماده است.")
        else:
            send_message(chat_id, "❌ خطا در ساخت مدل.")
            print(result.stderr)
        # پاکسازی
        os.unlink(temp_img)
        if Path(output_obj).exists():
            os.unlink(output_obj)
    except Exception as e:
        send_message(chat_id, f"❌ خطا: {e}")
        print(e)

print("🤖 ربات Polling شروع به کار کرد...")
while True:
    try:
        resp = requests.get(f"{BASE_URL}/getUpdates", params={"offset": last_update_id+1, "timeout": 30}, timeout=35)
        data = resp.json()
        for update in data.get("result", []):
            last_update_id = update["update_id"]
            msg = update.get("message")
            if not msg:
                continue
            chat_id = msg["chat"]["id"]
            if "photo" in msg:
                file_id = msg["photo"][-1]["file_id"]
                send_message(chat_id, "🔄 در حال ساخت مدل سه‌بعدی...")
                process_photo(chat_id, file_id)
            elif "text" in msg and msg["text"].strip() == "/start":
                send_message(chat_id, "سلام! تصویر مگس را بفرستید تا مدل سه‌بعدی ساخته شود.")
    except Exception as e:
        print("Error in loop:", e)
    time.sleep(1)
