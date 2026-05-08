import os
import io
import json
import time
import requests
from pathlib import Path
from PIL import Image
from engine_3d import Engine3D

# ---------- تنظیمات ----------
API_TOKEN = "659328109:njOuHvDe4jLuTprX7d9QQJfxnjzJpiUqOZY"   # توکن واقعی ربات
BASE_URL = f"https://api.bale.ai/bot{API_TOKEN}"
OUTPUT_DIR = Path("public/models")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_FILE = OUTPUT_DIR / "3d_object.obj"
STATE_FILE = "user_payments.json"       # ذخیره وضعیت پرداخت کاربران
PREVIEW_BASE_URL = "https://bale-3d-bot.vercel.app/preview.html"   # آدرس صفحه نمایش (اختیاری)

# ---------- توابع کمکی ----------
def load_json(filepath, default=None):
    if not os.path.exists(filepath):
        return default if default is not None else {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = json.dumps(keyboard)
    try:
        resp = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=15)
        return resp.ok
    except Exception as e:
        print(f"send_message error: {e}")
        return False

def send_file(chat_id, file_path, caption=""):
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": chat_id, "caption": caption}
            resp = requests.post(f"{BASE_URL}/sendDocument", data=data, files=files, timeout=60)
            return resp.ok
    except Exception as e:
        print(f"send_file error: {e}")
        return False

def send_invoice(chat_id, amount_tomans, label, description="تبدیل تصویر به مدل سه‌بعدی"):
    """ارسال فاکتور پرداخت واقعی (در صورت وجود provider_token معتبر)"""
    provider_token = "WALLET-as6NfAMYM6r5ZKUv"   # در حالت واقعی جایگزین کنید
    payload = {
        "chat_id": chat_id,
        "title": "شارژ حساب ربات سه‌بعدی",
        "description": description,
        "payload": f"order_{chat_id}_{int(time.time())}",
        "provider_token": provider_token,
        "currency": "IRR",
        "prices": json.dumps([{"label": label, "amount": amount_tomans * 10}])
    }
    try:
        resp = requests.post(f"{BASE_URL}/sendInvoice", json=payload, timeout=15)
        return resp.ok
    except Exception as e:
        print(f"send_invoice error: {e}")
        return False

def answer_callback(callback_id, text, show_alert=False):
    data = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert
    }
    try:
        requests.post(f"{BASE_URL}/answerCallbackQuery", json=data, timeout=10)
    except Exception as e:
        print(f"answer_callback error: {e}")

def download_and_grayscale(file_id, dest_path):
    try:
        resp = requests.get(f"{BASE_URL}/getFile", params={"file_id": file_id}, timeout=20)
        data = resp.json()
        if not data.get("ok"):
            return False
        file_path = data["result"]["file_path"]
        dl_url = f"https://api.bale.ai/file/bot{API_TOKEN}/{file_path}"
        r = requests.get(dl_url, timeout=30)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content))
        if img.mode != 'L':
            img = img.convert('L')
        img.save(dest_path, "JPEG")
        return True
    except Exception as e:
        print(f"download_and_grayscale error: {e}")
        return False

def generate_3d_model(image_path, output_obj_path):
    try:
        engine = Engine3D()
        success, result = engine.process(image_path, str(output_obj_path))
        if success and output_obj_path.exists() and output_obj_path.stat().st_size > 0:
            return True, "مدل با موفقیت ساخته شد."
        else:
            return False, f"خطا در تولید مدل: {result}"
    except Exception as e:
        return False, f"خطا در موتور سه‌بعدی: {e}"

def mark_paid(chat_id):
    data = load_json(STATE_FILE, {})
    data[str(chat_id)] = {"paid": True, "time": time.time()}
    save_json(STATE_FILE, data)

def is_paid(chat_id):
    data = load_json(STATE_FILE, {})
    return data.get(str(chat_id), {}).get("paid", False)

def get_preview_link(chat_id):
    return PREVIEW_BASE_URL

# ---------- مدیریت پیام‌ها ----------
def handle_update(update):
    if "message" in update:
        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        if not chat_id:
            return

        if "text" in msg and msg["text"].strip() == "/start":
            keyboard = {
                "inline_keyboard": [
                    [{"text": "💰 خرید اشتراک (۱ بار)", "callback_data": "buy_1"}],
                    [{"text": "📊 وضعیت پرداخت", "callback_data": "check_paid"}],
                    [{"text": "🔗 نمایش مدل سیمی", "callback_data": "get_preview"}]
                ]
            }
            send_message(chat_id, "سلام! تصویر خود را بفرستید تا مدل سه‌بعدی ساخته شود.\nپس از ساخت، می‌توانید مدل را به صورت سیمی ببینید و پس از پرداخت، فایل OBJ را دانلود کنید.", keyboard)
            return

        # دریافت تصویر
        file_id = None
        if "photo" in msg:
            file_id = msg["photo"][-1]["file_id"]
        elif "document" in msg and msg["document"].get("mime_type", "").startswith("image"):
            file_id = msg["document"]["file_id"]

        if file_id:
            temp_image = f"/tmp/input_{chat_id}_{int(time.time())}.jpg"
            if not download_and_grayscale(file_id, temp_image):
                send_message(chat_id, "خطا در دریافت تصویر. لطفاً دوباره تلاش کنید.")
                return

            send_message(chat_id, "✅ تصویر دریافت شد. در حال ساخت مدل سه‌بعدی...")

            success, msg_res = generate_3d_model(temp_image, MODEL_FILE)
            try: os.remove(temp_image)
            except: pass

            if not success:
                send_message(chat_id, f"❌ {msg_res}")
                return

            send_message(chat_id, "✅ مدل سه‌بعدی ساخته شد. حالا می‌توانید:")
            preview_link = get_preview_link(chat_id)
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎬 نمایش مدل سیمی (wireframe)", "url": preview_link}],
                    [{"text": "💰 پرداخت و دانلود فایل", "callback_data": "buy_1"}]
                ]
            }
            send_message(chat_id, "برای مشاهده مدل به صورت سه‌بعدی روی دکمه اول کلیک کنید.\nپس از پرداخت، فایل OBJ قابل دانلود خواهد بود.", keyboard)
            return

        send_message(chat_id, "لطفاً یک تصویر ارسال کنید یا از /start استفاده کنید.")

    elif "callback_query" in update:
        cb = update["callback_query"]
        data = cb.get("data")
        chat_id = cb.get("from", {}).get("id")
        cb_id = cb.get("id")
        if not chat_id:
            return

        if data == "buy_1":
            # ارسال فاکتور پرداخت (5000 تومان)
            if send_invoice(chat_id, 5000, "یک بار تبدیل", "پرداخت برای دریافت فایل سه‌بعدی"):
                answer_callback(cb_id, "فاکتور پرداخت ارسال شد. لطفاً آن را نهایی کنید.")
            else:
                answer_callback(cb_id, "خطا در ارسال فاکتور. لطفاً بعداً تلاش کنید.", True)

        elif data == "check_paid":
            if is_paid(chat_id):
                answer_callback(cb_id, "شما قبلاً پرداخت کرده‌اید. می‌توانید مدل را دانلود کنید.", True)
                # ارسال فایل OBJ مستقیماً (بدون نیاز به دکمه جدا)
                if MODEL_FILE.exists():
                    send_file(chat_id, str(MODEL_FILE), caption="مدل سه‌بعدی شما – با تشکر از پرداخت")
                else:
                    send_message(chat_id, "❌ مدل ساخته نشده است. لطفاً دوباره تصویر بفرستید.")
            else:
                answer_callback(cb_id, "هنوز پرداختی انجام نشده است. لطفاً ابتدا پرداخت کنید.", True)

        elif data == "download_model":
            if is_paid(chat_id) and MODEL_FILE.exists():
                send_file(chat_id, str(MODEL_FILE), caption="مدل سه‌بعدی شما – با تشکر از پرداخت")
                answer_callback(cb_id, "فایل مدل ارسال شد.")
            else:
                answer_callback(cb_id, "ابتدا باید پرداخت کنید و مدل هنوز وجود ندارد.", True)

        elif data == "get_preview":
            preview_link = get_preview_link(chat_id)
            answer_callback(cb_id, f"لینک نمایش مدل: {preview_link}")
        else:
            answer_callback(cb_id, "دستور نامشخص", True)

    # تأیید پرداخت موفق (pre_checkout_query)
    elif "pre_checkout_query" in update:
        pre = update["pre_checkout_query"]
        requests.post(f"{BASE_URL}/answerPreCheckoutQuery", json={
            "pre_checkout_query_id": pre["id"],
            "ok": True
        })
    elif "message" in update and "successful_payment" in update["message"]:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        mark_paid(chat_id)
        send_message(chat_id, "✅ پرداخت شما با موفقیت انجام شد. اکنون مدل OBJ برای شما ارسال می‌شود.")
        # ارسال فایل OBJ پس از پرداخت موفق
        if MODEL_FILE.exists():
            send_file(chat_id, str(MODEL_FILE), caption="مدل سه‌بعدی شما – با تشکر از پرداخت")
        else:
            send_message(chat_id, "❌ متأسفانه مدل ساخته نشده است. لطفاً دوباره تصویر خود را ارسال کنید.")

# ---------- حلقه اصلی ----------
def main_loop():
    last_id = 0
    print("ربات Bale 2D to 3D با پشتیبانی پرداخت و دانلود خودکار شروع به کار کرد...")
    while True:
        try:
            resp = requests.get(f"{BASE_URL}/getUpdates", params={
                "offset": last_id + 1,
                "timeout": 30
            }, timeout=35)
            data = resp.json()
            if not data.get("ok"):
                print("API error:", data)
                time.sleep(2)
                continue
            updates = data.get("result", [])
            for update in updates:
                last_id = update["update_id"]
                handle_update(update)
        except Exception as e:
            print(f"Error in main_loop: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main_loop()
