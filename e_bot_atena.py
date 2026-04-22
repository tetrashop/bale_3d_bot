import os
import io
import json
import time
import random
import requests
import subprocess
from typing import Optional
from PIL import Image
import numpy as np
BASE_DIR = "/data/data/com.termux/files/home/tetrashop-projects/projects/2d-to-3d"
RHETORIC_CORE = os.path.join(BASE_DIR, "pages-deploy/common-rhetoric-pro/rhetoric_engine")
OUTPUT_DIR = os.path.join(BASE_DIR, "public")
STATE_FILE = os.path.join(BASE_DIR, ".entropy_state.json")
BALANCES_FILE = os.path.join(BASE_DIR, ".user_balances.json")
API_TOKEN = "659328109:yyZ8HU6jJZDWZd-SBFun2ruMoLLQRtvnM2A"
BASE_URL = f"https://api.bale.ai/bot{API_TOKEN}"
PROVIDER_TOKEN = "WALLET-as6NfAMYM6r5ZKUv"
PRICES = {
"1_credit": 5000,
"10_credits": 40000
}
class ChaosNeutralizer:
    @staticmethod
    def get_ambiguous_delay(error_level: float) -> float:
        return random.uniform(2, 5) * error_level
        @staticmethod
        def atomic_flush(chat_id: int) -> None:
            if not os.path.exists(OUTPUT_DIR):
                return
                for f in os.listdir(OUTPUT_DIR):
                    if str(chat_id) in f or f.startswith("temp_"):
                        try:
                            os.remove(os.path.join(OUTPUT_DIR, f))
                        except Exception:
                            pass
                            class RevenueManager:
                                def load_balances(self) -> dict:
                                    if not os.path.exists(BALANCES_FILE):
                                        return {}
                                        try:
                                            with open(BALANCES_FILE, "r") as f:
                                                return json.load(f)
                                            except Exception:
                                                return {}
                                                def save_balances(self, balances: dict) -> None:
                                                    try:
                                                        with open(BALANCES_FILE, "w") as f:
                                                            json.dump(balances, f)
                                                        except Exception as e:
                                                            print(f"❌ خطا در ذخیره موجودیها: {e}")
                                                            def increase_balance(self, chat_id: int, credits: int) -> None:
                                                                balances = self.load_balances()
                                                                balances[str(chat_id)] = balances.get(str(chat_id), 0) + credits
                                                                self.save_balances(balances)
                                                                def decrease_balance(self, chat_id: int, credits: int) -> bool:
                                                                    balances = self.load_balances()
                                                                    current = balances.get(str(chat_id), 0)
                                                                    if current >= credits:
                                                                        balances[str(chat_id)] = current - credits
                                                                        self.save_balances(balances)
                                                                        return True
                                                                        return False
                                                                        def get_balance(self, chat_id: int) -> int:
                                                                            balances = self.load_balances()
                                                                            return balances.get(str(chat_id), 0)
                                                                            revenue_manager = RevenueManager()
                                                                            def convert_bytes_to_grayscale_array(image_bytes):
                                                                                img = Image.open(io.BytesIO(image_bytes)).convert("L")
                                                                                return np.array(img)
                                                                                class TetrashopAlwaysCorrect:
                                                                                    def __init__(self):
                                                                                        self.session = requests.Session()
                                                                                        self.session.headers.update({'Connection': 'keep-alive'})
                                                                                        os.makedirs(OUTPUT_DIR, exist_ok=True)
                                                                                        def process_with_rhetoric(self, img_path: str, chat_id: int) -> Optional[str]:
                                                                                            out_obj = os.path.join(OUTPUT_DIR, f"result_{chat_id}_{int(time.time())}.obj")
                                                                                            try:
                                                                                                cmd = ["nice", "-n", "19", RHETORIC_CORE, img_path, "--output", out_obj, "--optimized"]
                                                                                                subprocess.run(cmd, check=True, capture_output=True, timeout=150)
                                                                                                if os.path.exists(out_obj):
                                                                                                    return out_obj
                                                                                                    print(f"⚠️ فایل خروجی مدل سهبعدی برای کاربر {chat_id} ایجاد نشد.")
                                                                                                except Exception as e:
                                                                                                    print(f"🌀 خطا در پردازش مدل سهبعدی: {e}")
                                                                                                    return None
                                                                                                    def send_message(self, chat_id: int, text: str) -> None:
                                                                                                        data = {"chat_id": chat_id, "text": text}
                                                                                                        try:
                                                                                                            self.session.post(f"{BASE_URL}/sendMessage", data=data)
                                                                                                        except Exception as e:
                                                                                                            print(f"❌ خطا در ارسال پیام به {chat_id}: {e}")
                                                                                                            def send_file(self, chat_id: int, file_path: str, caption: Optional[str] = None) -> None:
                                                                                                                try:
                                                                                                                    with open(file_path, "rb") as f:
                                                                                                                        data = {"chat_id": chat_id}
                                                                                                                        if caption:
                                                                                                                            data["caption"] = caption
                                                                                                                            self.session.post(f"{BASE_URL}/sendDocument", data=data, files={"document": f})
                                                                                                                        except Exception as e:
                                                                                                                            print(f"❌ خطا در ارسال فایل به {chat_id}: {e}")
                                                                                                                            def send_invoice(self, chat_id: int, amount: int, label: str) -> None:
                                                                                                                                invoice_payload = {
                                                                                                                                "chat_id": chat_id,
                                                                                                                                "title": "شارژ حساب کاربری",
                                                                                                                                "description": f"خرید {label} برای تبدیل تصاویر به مدل ۳بعدی",
                                                                                                                                "payload": f"order_{chat_id}_{int(time.time())}",
                                                                                                                                "provider_token": PROVIDER_TOKEN,
                                                                                                                                "currency": "IRR",
                                                                                                                                "prices": json.dumps([{"label": label, "amount": amount * 10}])
                                                                                                                                }
                                                                                                                                try:
                                                                                                                                    self.session.post(f"{BASE_URL}/sendInvoice", data=invoice_payload)
                                                                                                                                except Exception as e:
                                                                                                                                    print(f"❌ خطا در ارسال فاکتور به {chat_id}: {e}")
                                                                                                                                    def answer_callback_query(self, callback_query_id: str, text: str, show_alert: bool = False) -> None:
                                                                                                                                        data = {
                                                                                                                                        "callback_query_id": callback_query_id,
                                                                                                                                        "text": text,
                                                                                                                                        "show_alert": show_alert
                                                                                                                                        }
                                                                                                                                        try:
                                                                                                                                            self.session.post(f"{BASE_URL}/answerCallbackQuery", data=data)
                                                                                                                                        except Exception as e:
                                                                                                                                            print(f"❌ خطا در پاسخ به کالبک: {e}")
                                                                                                                                            def is_outside_country(ip: Optional[str] = None) -> bool:
                                                                                                                                                try:
                                                                                                                                                    resp = requests.get("https://ipinfo.io/json" if ip is None else f"https://ipinfo.io/{ip}/json", timeout=5)
                                                                                                                                                    country = resp.json().get("country", "").upper()
                                                                                                                                                    return country != "IR"
                                                                                                                                                except Exception:
                                                                                                                                                    return False
                                                                                                                                                    def send_main_menu(bot: TetrashopAlwaysCorrect, chat_id: int) -> None:
                                                                                                                                                        text = (
                                                                                                                                                        "سلام به دنیای ۳بعدی رامین اجلال خوش آمدید! 🌟\n"
                                                                                                                                                        "این ربات ویدیو یا عکس شما را به مدل سهبعدی تبدیل میکند.\n"
                                                                                                                                                        "لطفاً برای شروع یا خرید اعتبار از گزینههای زیر استفاده کنید.\n\n"
                                                                                                                                                        "🆔 شناسه:\nhttps://ble.ir/2to3bot\n\n"
                                                                                                                                                        "برای سفارش:\n"
                                                                                                                                                        "۱. ویدیو یا عکس ارسال کنید.\n"
                                                                                                                                                        "۲. اعتبار لازم را بخرید.\n"
                                                                                                                                                        "۳. مدل سهبعدی را دریافت کنید."
                                                                                                                                                        )
                                                                                                                                                        keyboard = {
                                                                                                                                                        "inline_keyboard": [
                                                                                                                                                        [{"text": "💰 خرید اعتبار (۱ تبدیل ۵۰۰۰ تومان)", "callback_data": "buy_1"}],
                                                                                                                                                        [{"text": "💎 بسته ویژه (۱۰ تبدیل ۴۰۰۰۰ تومان)", "callback_data": "buy_10"}],
                                                                                                                                                        [{"text": "📊 استعلام موجودی", "callback_data": "check_balance"}]
                                                                                                                                                        ]
                                                                                                                                                        }
                                                                                                                                                        payload = {
                                                                                                                                                        "chat_id": chat_id,
                                                                                                                                                        "text": text,
                                                                                                                                                        "reply_markup": json.dumps(keyboard)
                                                                                                                                                        }
                                                                                                                                                        try:
                                                                                                                                                            bot.session.post(f"{BASE_URL}/sendMessage", data=payload)
                                                                                                                                                        except Exception as e:
                                                                                                                                                            print(f"❌ خطا در ارسال منو: {e}")
                                                                                                                                                            def main_loop() -> None:
                                                                                                                                                                bot = TetrashopAlwaysCorrect()
                                                                                                                                                                last_id = 0
                                                                                                                                                                if os.path.exists(STATE_FILE):
                                                                                                                                                                    try:
                                                                                                                                                                        with open(STATE_FILE, 'r') as f:
                                                                                                                                                                            last_id = json.load(f).get('id', 0)
                                                                                                                                                                        except Exception:
                                                                                                                                                                            last_id = 0
                                                                                                                                                                            print("☀️ ربات فعال شد.")
                                                                                                                                                                            while True:
                                                                                                                                                                                try:
                                                                                                                                                                                    resp = bot.session.get(
                                                                                                                                                                                    f"{BASE_URL}/getUpdates",
                                                                                                                                                                                    params={'offset': last_id + 1, 'timeout': 30},
                                                                                                                                                                                    timeout=45
                                                                                                                                                                                    )
                                                                                                                                                                                    if resp.status_code != 200:
                                                                                                                                                                                        time.sleep(ChaosNeutralizer.get_ambiguous_delay(1))
                                                                                                                                                                                        continue
                                                                                                                                                                                        updates = resp.json().get('result', [])
                                                                                                                                                                                        for u in updates:
                                                                                                                                                                                            last_id = u.get('update_id', last_id)
                                                                                                                                                                                            with open(STATE_FILE, "w") as f:
                                                                                                                                                                                                json.dump({'id': last_id}, f)
                                                                                                                                                                                                callback = u.get("callback_query")
                                                                                                                                                                                                if callback:
                                                                                                                                                                                                    chat_id = callback.get("from", {}).get("id")
                                                                                                                                                                                                    data = callback.get("data", "")
                                                                                                                                                                                                    if data == "buy_1":
                                                                                                                                                                                                        bot.send_invoice(chat_id, PRICES["1_credit"], "یک تبدیل")
                                                                                                                                                                                                        bot.answer_callback_query(callback.get("id"), "درگاه پرداخت یک تبدیل ارسال شد.")
                                                                                                                                                                                                    elif data == "buy_10":
                                                                                                                                                                                                        bot.send_invoice(chat_id, PRICES["10_credits"], "ده تبدیل")
                                                                                                                                                                                                        bot.answer_callback_query(callback.get("id"), "درگاه پرداخت بسته ده تایی ارسال شد.")
                                                                                                                                                                                                    elif data == "check_balance":
                                                                                                                                                                                                        bal = revenue_manager.get_balance(chat_id)
                                                                                                                                                                                                        bot.answer_callback_query(callback.get("id"), f"موجودی شما: {bal} اعتبار", True)
                                                                                                                                                                                                    else:
                                                                                                                                                                                                        bot.answer_callback_query(callback.get("id"), "دستور نامشخص.", True)
                                                                                                                                                                                                        continue
                                                                                                                                                                                                        msg = u.get("message", {})
                                                                                                                                                                                                        chat_id = msg.get("chat", {}).get("id")
                                                                                                                                                                                                        if not chat_id:
                                                                                                                                                                                                            continue
                                                                                                                                                                                                            if "pre_checkout_query" in u:
                                                                                                                                                                                                                pre = u.get("pre_checkout_query", {})
                                                                                                                                                                                                                bot.session.post(f"{BASE_URL}/answerPreCheckoutQuery",
                                                                                                                                                                                                                data={"pre_checkout_query_id": pre.get("id"), "ok": True})
                                                                                                                                                                                                                revenue_manager.increase_balance(pre.get("from", {}).get("id"), 1)
                                                                                                                                                                                                                continue
                                                                                                                                                                                                                if "successful_payment" in msg:
                                                                                                                                                                                                                    print(f"🛒 پرداخت موفق کاربر {chat_id}")
                                                                                                                                                                                                                    text = msg.get("text", "")
                                                                                                                                                                                                                    if text == "/start":
                                                                                                                                                                                                                        send_main_menu(bot, chat_id)
                                                                                                                                                                                                                        continue
                                                                                                                                                                                                                        if "photo" in msg or ("document" in msg and msg["document"].get("mime_type", "").startswith("image")):
                                                                                                                                                                                                                            balance = revenue_manager.get_balance(chat_id)
                                                                                                                                                                                                                            if balance < 1:
                                                                                                                                                                                                                                send_main_menu(bot, chat_id)
                                                                                                                                                                                                                                bot.send_message(chat_id, "اعتبار کافی ندارید. لطفاً ابتدا اعتبار بخرید.")
                                                                                                                                                                                                                                continue
                                                                                                                                                                                                                                try:
                                                                                                                                                                                                                                    f_id = None
                                                                                                                                                                                                                                    if "photo" in msg and msg["photo"]:
                                                                                                                                                                                                                                        f_id = msg["photo"][-1].get("file_id")
                                                                                                                                                                                                                                    elif "document" in msg:
                                                                                                                                                                                                                                        f_id = msg["document"].get("file_id")
                                                                                                                                                                                                                                        if not f_id:
                                                                                                                                                                                                                                            bot.send_message(chat_id, "خطا: فایل عکس پیدا نشد.")
                                                                                                                                                                                                                                            continue
                                                                                                                                                                                                                                            f_info = bot.session.get(f"{BASE_URL}/getFile", params={"file_id": f_id}).json()
                                                                                                                                                                                                                                            if not f_info.get("ok"):
                                                                                                                                                                                                                                                bot.send_message(chat_id, "خطا در دریافت اطلاعات فایل!")
                                                                                                                                                                                                                                                continue
                                                                                                                                                                                                                                                img_url = f'https://api.bale.ai/file/bot{API_TOKEN}/{f_info["result"]["file_path"]}'
                                                                                                                                                                                                                                                img_response = bot.session.get(img_url)
                                                                                                                                                                                                                                                img_response.raise_for_status()
                                                                                                                                                                                                                                                img_array = convert_bytes_to_grayscale_array(img_response.content)
                                                                                                                                                                                                                                                local_img = os.path.join(OUTPUT_DIR, f"raw_{chat_id}_{int(time.time())}.jpg")
                                                                                                                                                                                                                                                with open(local_img, "wb") as f_img:
                                                                                                                                                                                                                                                    f_img.write(img_response.content)
                                                                                                                                                                                                                                                    bot.send_message(chat_id, "عکس شما دریافت شد. در حال پردازش مدل سهبعدی...")
                                                                                                                                                                                                                                                    ChaosNeutralizer.atomic_flush(chat_id)
                                                                                                                                                                                                                                                    user_ip = None  # IP واقعی اگر در دسترس بود
                                                                                                                                                                                                                                                    if is_outside_country(user_ip):
                                                                                                                                                                                                                                                        obj_file = bot.process_with_rhetoric(local_img, chat_id)
                                                                                                                                                                                                                                                    else:
                                                                                                                                                                                                                                                        bot.send_message(chat_id, "فعلاً تبدیل مدل فقط برای خارج از کشور فعال است.")
                                                                                                                                                                                                                                                        continue
                                                                                                                                                                                                                                                        if obj_file and os.path.exists(obj_file):
                                                                                                                                                                                                                                                            revenue_manager.decrease_balance(chat_id, 1)
                                                                                                                                                                                                                                                            bot.send_file(chat_id, obj_file, caption="✅ مدل شما آماده است.")
                                                                                                                                                                                                                                                            bal = revenue_manager.get_balance(chat_id)
                                                                                                                                                                                                                                                            bot.send_message(chat_id, f"اعتبار شما باقی مانده: {bal}")
                                                                                                                                                                                                                                                        else:
                                                                                                                                                                                                                                                            bot.send_message(chat_id, "خطا در پردازش مدل، لطفاً بعدا تلاش کنید.")
                                                                                                                                                                                                                                                        except Exception as e:
                                                                                                                                                                                                                                                            logger.error(f"خطا در پردازش عکس: {e}")
                                                                                                                                                                                                                                                            bot.send_message(chat_id, "خطایی در پردازش عکس شما رخ داد.")
                                                                                                                                                                                                                                                            continue
                                                                                                                                                                                                                                                            bot.send_message(chat_id, "دستور نامشخص. لطفا /start یا از منو استفاده کنید.")
                                                                                                                                                                                                                                                            if __name__ == "__main__":
                                                                                                                                                                                                                                                                main_loop()
