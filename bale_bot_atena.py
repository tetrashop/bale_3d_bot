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
from datetime import datetime, timedelta

import trimesh  # نصب: pip install trimesh

BASE_DIR = os.getenv("BASE_DIR", "/data/data/com.termux/files/home/bale_3d_bot")
OUTPUT_DIR = os.path.join(BASE_DIR, "public")
STATE_FILE = os.path.join(BASE_DIR, ".entropy_state.json")
BALANCES_FILE = os.path.join(BASE_DIR, ".user_balances.json")
OFFLINE_INPUT_DIR = os.path.join(BASE_DIR, "offline_inputs")

API_TOKEN = os.getenv("API_TOKEN", "659328109:jXhU2N0eRJbkw2bpwfDdZm7XyIq4kFiIUoE")
BASE_URL = f"https://api.bale.ai/bot{API_TOKEN}"
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN", "WALLET-as6NfAMYM6r5ZKUv")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger()

for directory in [OUTPUT_DIR, OFFLINE_INPUT_DIR]:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Directory ensured: {directory}")

class RevenueManager:
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
SUPPORTED_3D_FORMATS = (".obj", ".stl", ".ply")

def is_supported_3d_file(filename: str) -> bool:
    return filename.lower().endswith(SUPPORTED_3D_FORMATS)

def get_model_info(file_path: str) -> Optional[str]:
    try:
        mesh = trimesh.load(file_path, force='mesh')
        vertices = len(mesh.vertices)
        faces = len(mesh.faces)
        info = f"مدل سه‌بعدی بارگذاری شد:\nراس‌ها: {vertices}\nمثلث‌ها: {faces}"
        return info
    except Exception as e:
        logger.error(f"Error loading 3D model for info: {e}")
        return None

def cleanup_old_models(directory: str, days: int = 7):
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                try:
                    os.remove(path)
                    logger.info(f"Removed old model file: {path}")
                except Exception as e:
                    logger.warning(f"Failed to remove old model {path}: {e}")

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

    def generate_thumbnail(self, obj_path: str, thumb_path: str) -> bool:
        try:
            mesh = trimesh.load(obj_path, force='mesh')
            scene = mesh.scene()
            png = scene.save_image(resolution=[320, 240])
            with open(thumb_path, "wb") as f:
                f.write(png)
            logger.info(f"Thumbnail created: {thumb_path}")
            return True
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return False

    def process_with_rhetoric(self, img_path: str, chat_id: int, algorithm: str = "default") -> Optional[str]:
        out_obj = os.path.join(OUTPUT_DIR, f"model_{chat_id}_{int(time.time())}.obj")
        try:
            cmd = [
                "nice", "-n", "19",
                os.path.join(BASE_DIR, "pages-deploy/common-rhetoric-pro/rhetoric_engine"),
                img_path, "--output", out_obj, "--optimized"
            ]
            if algorithm != "default":
                cmd.append(f"--algo={algorithm}")

            subprocess.run(cmd, check=True, capture_output=True, timeout=150)

            if os.path.exists(out_obj):
                self.send_message_with_fallback(chat_id, "مدل سه‌بعدی شما ساخته شد. در حال آماده‌سازی پیش‌نمایش...")
                thumb_path = out_obj.rsplit(".", 1)[0] + "_thumb.png"
                if self.generate_thumbnail(out_obj, thumb_path):
                    self.send_file_with_fallback(chat_id, thumb_path, caption="پیش‌نمایش مدل شما")
                return out_obj
            else:
                self.send_message_with_fallback(chat_id, "خطا در ساخت مدل سه‌بعدی.")
        except Exception as e:
            logger.error(f"Rhetoric processing error: {e}")
            self.send_message_with_fallback(chat_id, "خطا در ساخت مدل سه‌بعدی.")
        return None

    def process_offline_and_send(self, img_or_obj_path, chat_id: int) -> bool:
        if is_supported_3d_file(img_or_obj_path):
            info = get_model_info(img_or_obj_path)
            if info:
                self.send_message_with_fallback(chat_id, info)
            self.send_file_with_fallback(chat_id, img_or_obj_path, caption="مدل سه‌بعدی شما")
            return True

        # برای تصاویر: فرض می‌شود img_or_obj_path آرایه np یا مسیر تصویر باشد
        try:
            import engine_3d
        except ImportError:
            logger.error("engine_3d module not found.")
            self.send_message_with_fallback(chat_id, "خطا: ماژول تولید مدل آفلاین پیدا نشد.")
            return False

        # اگر مسیر است، تصویر را بارگذاری کنیم
        if isinstance(img_or_obj_path, str):
            img = Image.open(img_or_obj_path).convert("L")
            img_array = np.array(img)
        else:
            img_array = img_or_obj_path

        success, model_data = engine_3d.generate_model_offline(img_array)
        if success:
            obj_file = os.path.join(OUTPUT_DIR, f"offline_model_{chat_id}_{int(time.time())}.obj")
            try:
                with open(obj_file, "w") as f:
                    f.write(model_data)
                self.send_message_with_fallback(chat_id, "مدل آفلاین ساخته و ارسال شد.")
                self.send_file_with_fallback(chat_id, obj_file, caption="مدل آفلاین شما")
                thumb_path = obj_file.rsplit(".", 1)[0] + "_thumb.png"
                self.generate_thumbnail(obj_file, thumb_path)
                self.send_file_with_fallback(chat_id, thumb_path, caption="پیش‌نمایش مدل آفلاین")
                return True
            except Exception as e:
                logger.error(f"Offline model save/send error: {e}")
                self.send_message_with_fallback(chat_id, "خطا در ارسال مدل آفلاین.")
                return False
        else:
            self.send_message_with_fallback(chat_id, f"خطا در ساخت مدل آفلاین: {model_data}")
            return False
# مدیریت وضعیت کاربران (در عمل پایگاه داده بهتر است)
user_state = {}

def clear_user_data(user_id):
    # پاکسازی داده‌های کاربر (فایل/کش/حافظه)
    if user_id in user_state:
        del user_state[user_id]
    # می‌توانید اینجا پاکسازی فایل‌های موقت مرتبط با کاربر را هم اجرا کنید

def send_main_menu(user_id):
    keyboard = {
        "type": "keyboard",
        "buttons": [
            [{"type": "text", "text": "ساخت مدل آفلاین"}],
            [{"type": "text", "text": "مدل از ویدئو"}],
            [{"type": "text", "text": "راهنما"}]
        ],
        "resize": True,
        "one_time_keyboard": False
    }
    url = f"https://api.bale.ai/bot{API_TOKEN}/message/send"
    data = {
        "receiver": str(user_id),
        "type": "text",
        "content": {
            "text": "منوی اصلی ربات:",
            "keyboard": keyboard
        }
    }
    try:
        resp = requests.post(url, json=data, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"send_main_menu error: {e}")

def handle_update(update, bot: TetrashopAlwaysCorrect):
    message = update.get("message")
    if not message:
        return

    user_id = message["from"]["id"]
    text = message.get("text", "")
    photo = message.get("photo")
    video = message.get("video")

    if text == "/reset":
        clear_user_data(user_id)
        user_state[user_id] = "MAIN_MENU"
        bot.send_message_with_fallback(user_id, "ربات با موفقیت ریست شد.")
        send_main_menu(user_id)
        return

    # وضعیت کاربر
    state = user_state.get(user_id, "MAIN_MENU")

    if state == "MAIN_MENU":
        if text == "ساخت مدل آفلاین":
            bot.send_message_with_fallback(user_id, "لطفا یک تصویر ارسال کنید.")
            user_state[user_id] = "AWAIT_IMAGE_OFFLINE"
            return
        elif text.startswith("مدل از ویدئو") or text == "مدل از ویدئو":
            bot.send_message_with_fallback(user_id, "لطفا ویدئو ارسال کنید یا مسیر را تایپ کنید.")
            user_state[user_id] = "AWAIT_VIDEO"
            return
        elif text == "راهنما":
            help_text = "برای ساخت مدل از تصویر، گزینه 'ساخت مدل آفلاین' را بزنید و تصویر ارسال کنید.\n" \
                        "برای ساخت مدل از ویدئو، گزینه مربوطه را انتخاب کنید.\n" \
                        "برای ریست ربات: /reset"
            bot.send_message_with_fallback(user_id, help_text)
            return
        else:
            bot.send_message_with_fallback(user_id, "منوی اصلی، لطفا یکی از گزینه‌ها را انتخاب کنید.")
            send_main_menu(user_id)
            return

    elif state == "AWAIT_IMAGE_OFFLINE":
        # دریافت تصویر برای مدل آفلاین
        if photo:
            file_info = photo[-1]
            file_id = file_info.get("file_id")
            local_img_path = os.path.join(OFFLINE_INPUT_DIR, f"image_{user_id}_{int(time.time())}.jpg")
            if download_file(bot.session, file_id, local_img_path):
                success = bot.process_offline_and_send(local_img_path, user_id)
                if success:
                    revenue_manager.decrease_balance(user_id, 1)
                else:
                    bot.send_message_with_fallback(user_id, "خطایی در ساخت مدل آفلاین رخ داد.")
            else:
                bot.send_message_with_fallback(user_id, "خطا در دریافت تصویر.")
        else:
            bot.send_message_with_fallback(user_id, "تصویر ارسال نشده. لطفا تصویر ارسال کنید.")
            return
        user_state[user_id] = "MAIN_MENU"
        send_main_menu(user_id)
        return

    elif state == "AWAIT_VIDEO":
        # دریافت ویدئو یا تایپ مسیر
        if video:
            file_id = video.get("file_id")
            local_video_path = os.path.join(OFFLINE_INPUT_DIR, f"video_{user_id}_{int(time.time())}.mp4")
            if download_file(bot.session, file_id, local_video_path):
                obj_file = bot.process_with_rhetoric(local_video_path, user_id)
                if obj_file:
                    revenue_manager.decrease_balance(user_id, 1)
                else:
                    bot.send_message_with_fallback(user_id, "خطا در ساخت مدل از ویدئو.")
            else:
                bot.send_message_with_fallback(user_id, "خطا در دریافت ویدئو.")
        elif text.startswith("مدل از ویدئو "):
            path = text[len("مدل از ویدئو "):].strip()
            if os.path.exists(path):
                obj_file = bot.process_with_rhetoric(path, user_id)
                if obj_file:
                    revenue_manager.decrease_balance(user_id, 1)
                else:
                    bot.send_message_with_fallback(user_id, "خطا در ساخت مدل از ویدئو.")
            else:
                bot.send_message_with_fallback(user_id, "مسیر ویدئو معتبر نیست.")
                return
        else:
            bot.send_message_with_fallback(user_id, "لطفا ویدئو ارسال کنید یا مسیر را وارد کنید.")
            return

        user_state[user_id] = "MAIN_MENU"
        send_main_menu(user_id)
        return

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

def main_loop():
    bot = TetrashopAlwaysCorrect()
    last_id = 0
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                last_id = json.load(f).get("id", 0)
    except Exception:
        last_id = 0

    logger.info("ربات شروع به کار کرد.")

    while True:
        resp = api_request_with_retry(bot.session, "GET", f"{BASE_URL}/getUpdates",
                                     params={"offset": last_id + 1, "timeout": 30},
                                     max_retry=3)
        if resp is None:
            if bot.online:
                logger.warning("Max retries reached, switching offline")
                bot.online = False
            # می‌توانید به شناسه چت پشتیبانی (support chat) اطلاع بدهید
            time.sleep(10)
            continue
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

                try:
                    handle_update(update, bot)
                except Exception as e:
                    logger.error(f"Error processing update: {e}")

if __name__ == "__main__":
    main_loop()
