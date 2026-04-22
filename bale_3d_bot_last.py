import os
import sys
import subprocess
import requests
import json
import time
import random
# ۱. پیکربندی استراتژیک در لایه پایداری (پروژه تتراشاپ ۱۴۰۵)
BASE_DIR = "/data/data/com.termux/files/home/tetrashop-projects/projects/2d-to-3d"
RHETORIC_CORE = os.path.join(
BASE_DIR, "pages-deploy/common-rhetoric-pro/rhetoric_engine"
)
OUTPUT_DIR = os.path.join(BASE_DIR, "public")
STATE_FILE = os.path.join(BASE_DIR, ".entropy_state.json")
API_TOKEN = "659328109:yyZ8HU6jJZDWZd-SBFun2ruMoLLQRtvnM2A"
BASE_URL = f"https://api.bale.ai/bot{API_TOKEN}"
class ChaosNeutralizer:
    """الگوریتم رو سفید کردن اغتشاش (نامعلومی هوشمند)"""
    @staticmethod
    def get_ambiguous_delay(error_level):
        """ایجاد تأخیر نامعلوم برای فریب اختلالات شبکه"""
        return random.uniform(2, 5) * error_level
        @staticmethod
        def atomic_flush(chat_id):
            """پاکسازی اتمیک برای جلوگیری از چندپارگی حافظه"""
            for ext in [".jpg", ".obj", ".tmp"]:
                if os.path.exists(OUTPUT_DIR):
                    for f in os.listdir(OUTPUT_DIR):
                        if str(chat_id) in f or f.startswith("temp_"):
                            try:
                                os.remove(os.path.join(OUTPUT_DIR, f))
                                except:
                                    pass
                                    class TetrashopAlwaysCorrect:
                                        def __init__(self):
                                            self.session = requests.Session()
                                            self.session.headers.update({"Connection": "keep-alive"})
                                            os.makedirs(OUTPUT_DIR, exist_ok=True)
                                            def process_with_rhetoric(self, img_path, chat_id):
                                                """هسته تبدیل: تبدیل اغتشاش به هندسه (استخراج دانش)"""
                                                out_obj = os.path.join(OUTPUT_DIR, f"result_{chat_id}_{int(time.time())}.obj")
                                                try:
                                                    # نیس کردن (Nice) پردازش برای پایداری در ترموکس
                                                    cmd = [
                                                    "nice",
                                                    "-n",
                                                    "19",
                                                    RHETORIC_CORE,
                                                    img_path,
                                                    "--output",
                                                    out_obj,
                                                    "--optimized",
                                                    ]
                                                    subprocess.run(cmd, check=True, capture_output=True, timeout=150)
                                                    return out_obj if os.path.exists(out_obj) else None
                                                except Exception as e:
                                                    print(f"🌀 اغتشاش در موتور خنثی شد: {e}")
                                                    return None
                                                    PRICES = {"1_credit": 5000, "10_credits": 40000}
                                                    def send_main_menu(chat_id):
                                                        """ارسال منوی اصلی بازو با دکمههای شیشهای"""
                                                        text = (
                                                        "🚀 به موتور استخراج هندسه اجلال خوش آمدید!\n\nلطفاً تصویر خود را ارسال کنید."
                                                        )
                                                        keyboard = {
                                                        "inline_keyboard": [
                                                        [{"text": "💰 خرید اعتبار (۱ تبدیل)", "callback_data": "buy_1"}],
                                                        [{"text": "💎 پکیج اقتصادی (۱۰ تبدیل)", "callback_data": "buy_10"}],
                                                        [{"text": "📊 استعلام موجودی", "callback_data": "check_balance"}],
                                                        ]
                                                        }
                                                        payload = {"chat_id": chat_id, "text": text, "reply_markup": json.dumps(keyboard)}
                                                        requests.post(f"{BASE_URL}/sendMessage", data=payload)
                                                        def send_invoice(chat_id, amount, label):
                                                            """ارسال فاکتور پرداخت به کاربر"""
                                                            invoice_payload = {
                                                            "chat_id": chat_id,
                                                            "title": "شارژ حساب کاربری",
                                                            "description": f"تهیه {label} برای تبدیل تصاویر به مدل ۳بعدی",
                                                            "payload": f"order_{chat_id}{int(time.time())}",
                                                            "provider_token": "YOUR_PAYMENT_TOKEN",
                                                            "currency": "IRR",
                                                            "prices": json.dumps([{"label": label, "amount": amount * 10}]),
                                                            }
                                                            requests.post(f"{BASE_URL}/sendInvoice", data=invoice_payload)
                                                            def main_loop():
                                                                bot = TetrashopAlwaysCorrect()
                                                                last_id = 0
                                                                if os.path.exists(STATE_FILE):
                                                                    try:
                                                                        with open(STATE_FILE, "r") as f:
                                                                            last_id = json.load(f)["id"]
                                                                            except:
                                                                                last_id = 0
                                                                                print("☀️ سیستم 'نامعلوم و همیشه درست' اجلال (۱۴۰۵) فعال گشت.")
                                                                                while True:
                                                                                    try:
                                                                                        resp = bot.session.get(
                                                                                        f"{BASE_URL}/getUpdates",
                                                                                        params={"offset": last_id + 1},
                                                                                        timeout=random.randint(30, 45),
                                                                                        )
                                                                                        if resp.status_code != 200:
                                                                                            time.sleep(ChaosNeutralizer.get_ambiguous_delay(1))
                                                                                            continue
                                                                                            updates = resp.json().get("result", [])
                                                                                            for u in updates:
                                                                                                last_id = u["update_id"]
                                                                                                with open(STATE_FILE, "w") as f:
                                                                                                    json.dump({"id": last_id}, f)
                                                                                                    msg = u.get("message", u.get("callback_query", {}).get("message", {}))
                                                                                                    chat_id = msg.get("chat", {}).get("id")
                                                                                                    if not chat_id:
                                                                                                        continue
                                                                                                        if "photo" in msg or (
                                                                                                        "document" in msg
                                                                                                        and msg.get("document", {}).get("mime_type", "").startswith("image")
                                                                                                        ):
                                                                                                            ChaosNeutralizer.atomic_flush(chat_id)
                                                                                                            try:
                                                                                                                f_id = msg.get("photo", [{}])[-1].get("file_id") or msg.get(
                                                                                                                "document", {}
                                                                                                                ).get("file_id")
                                                                                                                f_info = bot.session.get(
                                                                                                                f"{BASE_URL}/getFile", params={"file_id": f_id}
                                                                                                                ).json()
                                                                                                                if f_info.get("ok"):
                                                                                                                    img_url = f'https://api.bale.ai/file/bot{API_TOKEN}/{f_info["result"]["file_path"]}'
                                                                                                                    local_img = os.path.join(OUTPUT_DIR, f"raw{chat_id}.jpg")
                                                                                                                    with open(local_img, "wb") as f_img:
                                                                                                                        f_img.write(bot.session.get(img_url).content)
                                                                                                                        obj_file = bot.process_with_rhetoric(local_img, chat_id)
                                                                                                                        if obj_file:
                                                                                                                            with open(obj_file, "rb") as f_obj:
                                                                                                                                bot.session.post(
                                                                                                                                f"{BASE_URL}/sendDocument",
                                                                                                                                data={
                                                                                                                                "chat_id": chat_id,
                                                                                                                                "caption": "✅ استخراج دانش سهبعدی تکمیل شد.",
                                                                                                                                },
                                                                                                                                files={"document": f_obj},
                                                                                                                                timeout=180,
                                                                                                                                )
                                                                                                                                ChaosNeutralizer.atomic_flush(chat_id)
                                                                                                                            except Exception as inner_e:
                                                                                                                                print(f"⚠️ اغتشاش درونی مدیریت شد: {inner_e}")
                                                                                                                            elif "text" in msg and msg["text"] == "/start":
                                                                                                                                send_main_menu(chat_id)
                                                                                                                            except requests.exceptions.RequestException as e:
                                                                                                                                wait_time = ChaosNeutralizer.get_ambiguous_delay(2)
                                                                                                                                print(f"📡 اختلال شبکه خنثی شد. صبر برای {wait_time:.1f} ثانیه...")
                                                                                                                                time.sleep(wait_time)
                                                                                                                            except Exception as e:
                                                                                                                                print(f"❌ خطای پیشبینی نشده: {e}")
                                                                                                                                time.sleep(5)
                                                                                                                                if __name__ == "__main__":
                                                                                                                                    main_loop()
