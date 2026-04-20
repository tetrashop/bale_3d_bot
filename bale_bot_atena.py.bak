import os
import io
import json
import time
import logging
import requests
import socket
import glob
from typing import Optional
from PIL import Image
import numpy as np
import subprocess

BASE_DIR = os.getenv("BASE_DIR", "/data/data/com.termux/files/home/bale_3d_bot")
OUTPUT_DIR = os.path.join(BASE_DIR, "public")
STATE_FILE = os.path.join(BASE_DIR, ".entropy_state.json")
BALANCES_FILE = os.path.join(BASE_DIR, ".user_balances.json")
OFFLINE_INPUT_DIR = os.path.join(BASE_DIR, "offline_inputs")

API_TOKEN = os.getenv("API_TOKEN", "659328109:jXhU2N0eRJbkw2bpwfDdZm7XyIq4kFiIUoE")
BASE_URL = f"https://api.bale.ai/bot{API_TOKEN}"
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "WALLET-as6NfAMYM6r5ZKUv")
ENABLE_COUNTRY_LIMIT = bool(int(os.getenv("ENABLE_COUNTRY_LIMIT", "1")))

CHANNEL_ID = "@Abc123"  # شناسه کانال برای ارسال پیام با دکمه

PRICES = {"1_credit": 5000, "10_credits": 40000}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger()

for directory in [OUTPUT_DIR, OFFLINE_INPUT_DIR]:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Directory ensured: {directory}")

class RevenueManager:
    # ... (مدیریت اعتبار طبق بخش قبل)
    # منطق کامل افزایش، کاهش و خواندن اعتبار

    def load_balances(self) -> dict:
        if not os.path.exists(BALANCES_FILE):
            return {}
        try:
            with open(BALANCES_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Load balances error: {e}")
            return {}

    def save_balances(self, balances: dict):
        try:
            with open(BALANCES_FILE, "w") as f:
                json.dump(balances, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Save balances error: {e}")

    def increase_balance(self, chat_id: int, credits: int):
        balances = self.load_balances()
        key = str(chat_id)
        balances[key] = balances.get(key, 0) + credits
        self.save_balances(balances)
        logger.info(f"Balance increased for {chat_id}: +{credits}")

    def decrease_balance(self, chat_id: int, credits: int) -> bool:
        balances = self.load_balances()
        key = str(chat_id)
        if balances.get(key, 0) >= credits:
            balances[key] -= credits
            self.save_balances(balances)
            logger.info(f"Balance decreased for {chat_id}: -{credits}")
            return True
        return False

    def get_balance(self, chat_id: int) -> int:
        balances = self.load_balances()
        return balances.get(str(chat_id), 0)

revenue_manager = RevenueManager()

def test_online_connection():
    try:
        socket.gethostbyname("api.bale.ai")
        return True
    except Exception:
        return False

def api_request_with_retry(session, method, url, max_retry=5, **kwargs):
    delay = 1
    for attempt in range(max_retry):
        if not test_online_connection():
            logger.warning("DNS resolution failed, retrying...")
            time.sleep(10)
            continue
        try:
            resp = session.request(method, url, timeout=30, **kwargs)
            if resp.status_code == 200:
                return resp
            logger.warning(f"Status code {resp.status_code} at attempt {attempt+1}")
        except Exception as e:
            logger.warning(f"Request failed at attempt {attempt+1}: {e}")
        time.sleep(delay)
        delay *= 2
    logger.error(f"Max retries reached for URL: {url}")
    return None

class TetrashopAlwaysCorrect:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Connection": "keep-alive"})
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(OFFLINE_INPUT_DIR, exist_ok=True)
        self.online = True
        self.message_queue = []

    def send_message_with_fallback(self, chat_id: int, text: str):
        if self.online:
            try:
                url = f"https://api.bale.ai/bot{API_TOKEN}/message/send"
                json_data = {"receiver": str(chat_id), "type": "text", "content": {"text": text}}
                resp = api_request_with_retry(self.session, "POST", url, json=json_data)
                if resp is None:
                    raise Exception("Send failed")
                logger.info(f"Sent message to {chat_id}")
            except Exception as e:
                self.online = False
                self.message_queue.append(("text", chat_id, text))
                logger.warning(f"Send failed, message queued: {e}")
        else:
            self.message_queue.append(("text", chat_id, text))

    def send_file_with_fallback(self, chat_id: int, file_path: str, caption: Optional[str] = None):
        if self.online:
            url = f"https://api.bale.ai/bot{API_TOKEN}/file/upload"
            try:
                with open(file_path, "rb") as f:
                    data = {"receiver": str(chat_id)}
                    if caption:
                        data["caption"] = caption
                    resp = self.session.post(url, data=data, files={"file": f}, timeout=60)
                    if resp.status_code == 200:
                        logger.info(f"Sent file to {chat_id}")
                        return
                raise Exception(f"File upload failed with status {resp.status_code}")
            except Exception as e:
                self.online = False
                self.message_queue.append(("file", chat_id, file_path, caption))
                logger.warning(f"File send failed, file queued: {e}")
        else:
            self.message_queue.append(("file", chat_id, file_path, caption))

    def resend_queued_messages(self):
        if not self.online:
            return
        i = 0
        while i < len(self.message_queue):
            item = self.message_queue[i]
            try:
                if item[0] == "text":
                    _, chat_id, text = item
                    url = f"https://api.bale.ai/bot{API_TOKEN}/message/send"
                    data = {"receiver": str(chat_id), "type": "text", "content": {"text": text}}
                    resp = self.session.post(url, json=data, timeout=15)
                    resp.raise_for_status()
                    logger.info(f"Resent queued text message to {chat_id}")
                elif item[0] == "file":
                    _, chat_id, file_path, caption = item
                    url = f"https://api.bale.ai/bot{API_TOKEN}/file/upload"
                    with open(file_path, "rb") as f:
                        data = {"receiver": str(chat_id)}
                        if caption:
                            data["caption"] = caption
                        resp = self.session.post(url, data=data, files={"file": f}, timeout=60)
                        resp.raise_for_status()
                    logger.info(f"Resent queued file to {chat_id}")
                self.message_queue.pop(i)
            except Exception as e:
                logger.warning(f"Failed to resend message, going offline again: {e}")
                self.online = False
                break

    def process_with_rhetoric(self, img_path: str, chat_id: int) -> Optional[str]:
        out_obj = os.path.join(OUTPUT_DIR, f"model_{chat_id}_{int(time.time())}.obj")
        try:
            cmd = [
                "nice", "-n", "19", os.path.join(BASE_DIR, "pages-deploy/common-rhetoric-pro/rhetoric_engine"),
                img_path, "--output", out_obj, "--optimized"
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=150)
            if os.path.exists(out_obj):
                self.send_message_with_fallback(chat_id, "مدل سه‌بعدی شما ساخته شد.")
                return out_obj
            else:
                self.send_message_with_fallback(chat_id, "خطا در ساخت مدل سه‌بعدی.")
        except Exception as e:
            logger.error(f"Rhetoric processing error: {e}")
            self.send_message_with_fallback(chat_id, "خطا در ساخت مدل سه‌بعدی.")
        return None

    def process_offline_and_send(self, img_array, chat_id: int) -> bool:
        import engine_3d
        success, model_data = engine_3d.generate_model_offline(img_array)
        if success:
            obj_file = os.path.join(OUTPUT_DIR, f"offline_model_{chat_id}_{int(time.time())}.obj")
            try:
                with open(obj_file, "w") as f:
                    f.write(model_data)
                self.send_message_with_fallback(chat_id, "مدل آفلاین ساخته شد.")
                self.send_file_with_fallback(chat_id, obj_file, caption="مدل آفلاین شما")
                return True
            except Exception as e:
                self.send_message_with_fallback(chat_id, "خطا در ارسال مدل آفلاین.")
                logger.error(f"Offline model save/send error: {e}")
                return False
        else:
            self.send_message_with_fallback(chat_id, f"خطا در ساخت مدل آفلاین: {model_data}")
            return False

def process_offline_dir(bot: TetrashopAlwaysCorrect):
    files = glob.glob(os.path.join(OFFLINE_INPUT_DIR, "*.*"))
    for file_path in files:
        ext = file_path.rsplit('.', 1)[-1].lower()
        chat_id = 0
        try:
            if ext in ("jpg", "jpeg", "png"):
                img = Image.open(file_path).convert("L")
                img_array = np.array(img)
                if bot.process_offline_and_send(img_array, chat_id):
                    os.remove(file_path)
                    logger.info(f"Offline image processed and removed: {file_path}")
            elif ext in ("mp4", "avi", "mov"):
                obj_file = bot.process_with_rhetoric(file_path, chat_id)
                if obj_file and os.path.exists(obj_file):
                    os.remove(file_path)
                    logger.info(f"Offline video processed and removed: {file_path}")
        except Exception as e:
            logger.error(f"Error processing offline file {file_path}: {e}")

def ask_offline_mode(bot, chat_id: int):
    bot.send_message_with_fallback(chat_id, "سرویس آنلاین در دسترس نیست. لطفا 'بله' یا 'خیر' تایپ کنید.")


def download_file(session, file_id: str, local_path: str) -> bool:
    try:
        url = f"https://api.bale.ai/bot{API_TOKEN}/file/get"
        params = {"file_id": file_id}
        resp = session.get(url, params=params, timeout=60)
        if resp.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(resp.content)
            logger.info(f"File downloaded: {local_path}")
            return True
        else:
            logger.error(f"Failed to download file {file_id}: Status {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"Exception in download_file: {e}")
        return False

def send_payment_button(chat_id: int, amount: int):
    url = f"https://api.bale.ai/bot{API_TOKEN}/message/send"
    button = {
        "inline_keyboard": [[
            {
                "text": f"شارژ {amount} سکه",
                "callback_data": f"pay_{amount}"
            }
        ]]
    }
    data = {
        "receiver": str(chat_id),
        "type": "text",
        "content": {
            "text": f"برای شارژ {amount} سکه لطفا کلیک کنید",
            "keyboard": button
        }
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        if resp.status_code == 200:
            logger.info(f"Payment button sent to {chat_id}")
        else:
            logger.error(f"Failed to send payment button: {resp.status_code}")
    except Exception as e:
        logger.error(f"send_payment_button error: {e}")



# ذخیره وضعیت کاربران (در عمل باید پایگاه داده باشد)
user_state = {}


def handle_update(update):
    message = update.get("message")
    if not message:
        return

    user_id = message["from"]["id"]
    text = message.get("text", "")

    if text == "/reset":
        clear_user_data(user_id)
        user_state[user_id] = "MAIN_MENU"
        send_message(user_id, "ربات با موفقیت ریست شد.")
        send_main_menu(user_id)
        return

    # مدیریت پیام‌ها بر اساس وضعیت
    state = user_state.get(user_id, "MAIN_MENU")
    if state == "MAIN_MENU":
        # اینجا می‌توان منو را مدیریت کرد یا دستورات جدید اضافه نمود
        send_message(user_id, f"پیام دریافتی: {text}")


def clear_user_data(user_id):
    # اینجا پاکسازی داده‌های کاربر مثل فایل/کش/دیتابیس باشه
    # فعلاً به صورت نمونه فقط حذف وضعیت
    if user_id in user_state:
        del user_state[user_id]


def send_message(user_id, text):
    url = API_URL + "sendMessage"
    data = {
        "chat_id": user_id,
        "text": text
    }
    requests.post(url, json=data)


def send_main_menu(user_id):
    keyboard = {
        "type": "keyboard",
        "buttons": [
            [{"type": "text", "text": "گزینه ۱"}],
            [{"type": "text", "text": "گزینه ۲"}],
            [{"type": "text", "text": "راهنما"}]
        ],
        "resize": True,
        "one_time_keyboard": False
    }

    url = API_URL + "sendMessage"
    data = {
        "chat_id": user_id,
        "text": "منوی اصلی ربات:",
        "keyboard": keyboard
    }
    requests.post(url, json=data)


# نمونه دریافت وبهوک و پردازش (برای فریم‌ورک یا سرور خودت تغییر بده)
def webhook_handler(request_json):
    """
    فرض شده JSON درخواست ورودی ورسل یا هر جای دیگه به این تابع داده می‌شود.
    """
    update = request_json
    handle_update(update)
    return "ok"




def main_loop():
    import time
    bot = TetrashopAlwaysCorrect()
    last_id = 0
    notified_users = set()
    SUPPORT_CHAT_ID = 659328109

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                last_id = json.load(f).get("id", 0)
        except:
            last_id = 0

    while True:
        resp = api_request_with_retry(bot.session, "GET",
                                     f"{BASE_URL}/getUpdates",
                                     params={"offset": last_id + 1, "timeout": 30},
                                     max_retry=3)

        if resp is None:
            if bot.online:
                logger.warning("Max retries reached, switching offline")
            bot.online = False

            if SUPPORT_CHAT_ID not in notified_users:
                ask_offline_mode(bot, SUPPORT_CHAT_ID)
                notified_users.add(SUPPORT_CHAT_ID)

            while True:
                process_offline_dir(bot)
                time.sleep(10)
                if test_online_connection():
                    logger.info("Back online, resuming")
                    bot.online = True
                    bot.resend_queued_messages()
                    break
        else:
            if not bot.online:
                bot.online = True
                logger.info("Back online, resending queued messages")
                bot.resend_queued_messages()

            updates = resp.json().get("result", [])
            for update in updates:
                last_id = max(last_id, update.get("update_id", last_id))
                with open(STATE_FILE, "w") as f:
                    json.dump({"id": last_id}, f)
                # ادامه پردازش پیام و callback ها طبق ساختار خودتان

                message = update.get("message")
                if not message:
                    continue

                chat = message.get("chat")
                if not chat:
                    continue

                chat_id = chat.get("id")
                text = message.get("text")
                photo = message.get("photo")
                video = message.get("video")
    
                try:
                    if text:
                        txt = text.strip()
                        if txt == "سلام":
                            bot.send_message_with_fallback(chat_id, "سلام! چطورید؟")
                            continue

                    balance = revenue_manager.get_balance(chat_id)
                    cost_per_model = 1
            
                    if balance < cost_per_model:
                        bot.send_message_with_fallback(chat_id, "موجودی شما کافی نیست. لطفا اقدام به شارژ نمایید.")
                        continue
            
                    if txt == "ساخت مدل آفلاین":
                        bot.send_message_with_fallback(chat_id, "لطفا تصویر خود را ارسال کنید تا مدل آفلاین ساخته شود.")
                        continue

                    if txt.startswith("مدل از ویدئو"):
                        parts = txt.split(" ", 3)
                        if len(parts) < 4:
                             bot.send_message_with_fallback(chat_id, "لطفا مسیر ویدئو را وارد کنید: مدل از ویدئو <مسیر_ویدئو>")
                             continue
                        video_path = parts[3]
                        model_data = engine_3d.process_video_to_3d(video_path)
                        if model_data:
                            file_path = os.path.join(OUTPUT_DIR, f"model_{chat_id}_{int(time.time())}.obj")
                            with open(file_path, "wb") as f:
                                f.write(model_data)
                            revenue_manager.decrease_balance(chat_id, cost_per_model)
                            bot.send_file_with_fallback(chat_id, file_path, caption="مدل سه‌بعدی ساخته شده از ویدئو")
                        else:
                            bot.send_message_with_fallback(chat_id, "خطا در ساخت مدل از ویدئو.")
                            continue
            
                        bot.send_message_with_fallback(chat_id, f"پیام شما دریافت شد: {txt}")

                    elif photo:
                        file_info = photo[-1]
                        file_id = file_info.get("file_id")
                        local_img_path = os.path.join(OFFLINE_INPUT_DIR, f"image_{chat_id}_{int(time.time())}.jpg")
                        if download_file(bot.session, file_id, local_img_path):
                            success = bot.process_offline_and_send(local_img_path, chat_id)
                            if success:
                                revenue_manager.decrease_balance(chat_id, 1)
                            else:
                                bot.send_message_with_fallback(chat_id, "خطا در ساخت مدل آفلاین.")
                        else:
                            bot.send_message_with_fallback(chat_id, "خطا در دریافت تصویر.")
        
                    elif video:
                        file_id = video.get("file_id")
                        local_video_path = os.path.join(OFFLINE_INPUT_DIR, f"video_{chat_id}_{int(time.time())}.mp4")
                        if download_file(bot.session, file_id, local_video_path):
                            obj_file = bot.process_with_rhetoric(local_video_path, chat_id)
                            if obj_file:
                                revenue_manager.decrease_balance(chat_id, 1)
                            else:
                                bot.send_message_with_fallback(chat_id, "خطا در ساخت مدل از ویدئو.")
                        else:
                            bot.send_message_with_fallback(chat_id, "خطا در دریافت ویدئو.")
    
                    callback = update.get("callback_query")
                    if callback:
                        data = callback.get("data", "")
                        from_user = callback.get("from", {})
                        chat_id = from_user.get("id")

                    if data.startswith("pay_"):
                        amount = int(data.split("_")[1])
                    # فرض: افزودن اعتبار به کاربر
                    revenue_manager.increase_balance(chat_id, amount)
                    bot.send_message_with_fallback(chat_id, f"موجودی شما {amount} واحد افزایش یافت.")

                except Exception as e:
                    logger.error(f"Error processing message from {chat_id}: {e}")
                    bot.send_message_with_fallback(chat_id, "خطایی پیش آمد. لطفا دوباره تلاش کنید.")

if __name__ == "__main__":
    main_loop()
