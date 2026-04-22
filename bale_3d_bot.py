import os
import sys
import subprocess
import requests
import json
import time
import random
BASE_DIR = "/data/data/com.termux/files/home/tetrashop-projects/projects/2d-to-3d"
RHETORIC_CORE = os.path.join(
BASE_DIR, "pages-deploy/common-rhetoric-pro/rhetoric_engine"
)
OUTPUT_DIR = os.path.join(BASE_DIR, "public")
STATE_FILE = os.path.join(BASE_DIR, ".entropy_state.json")
API_TOKEN = "659328109:yyZ8HU6jJZDWZd-SBFun2ruMoLLQRtvnM2A"
BASE_URL = f"https://api.bale.ai/bot{API_TOKEN}"
class ChaosNeutralizer:
    @staticmethod
    def get_ambiguous_delay(error_level):
        return random.uniform(2, 5) * error_level
        @staticmethod
        def atomic_flush(chat_id):
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
                                    def send_message(self, chat_id, text):
                                        data = {"chat_id": chat_id, "text": text}
                                        try:
                                            return self.session.post(f"{BASE_URL}/sendMessage", data=data, timeout=15)
                                        except Exception as e:
                                            print(f"خطا در ارسال پیام: {e}")
                                            def send_file(self, chat_id, file_path, caption=None):
                                                try:
                                                    with open(file_path, "rb") as f:
                                                        files = {"document": f}
                                                        data = {"chat_id": chat_id}
                                                        if caption:
                                                            data["caption"] = caption
                                                            return self.session.post(
                                                            f"{BASE_URL}/sendDocument", data=data, files=files, timeout=180
                                                            )
                                                        except Exception as e:
                                                            print(f"خطا در ارسال فایل: {e}")
                                                            def process_with_rhetoric(self, img_path, chat_id):
                                                                out_obj = os.path.join(OUTPUT_DIR, f"result_{chat_id}_{int(time.time())}.obj")
                                                                try:
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
                                                                    def main_loop():
                                                                        bot = TetrashopAlwaysCorrect()
                                                                        last_id = 0
                                                                        if os.path.exists(STATE_FILE):
                                                                            try:
                                                                                with open(STATE_FILE, "r") as f:
                                                                                    last_id = json.load(f).get("id", 0)
                                                                                    except:
                                                                                        last_id = 0
                                                                                        print("☀️ سیستم 'نامعلوم و همیشه درست' اجلال (۱۴۰۵) فعال گشت.")
                                                                                        while True:
                                                                                            try:
                                                                                                resp = bot.session.get(
                                                                                                f"{BASE_URL}/getUpdates",
                                                                                                params={"offset": last_id + 1, "timeout": 30},
                                                                                                timeout=random.randint(40, 60),
                                                                                                )
                                                                                                if resp.status_code != 200:
                                                                                                    delay = ChaosNeutralizer.get_ambiguous_delay(1)
                                                                                                    time.sleep(delay)
                                                                                                    continue
                                                                                                    updates = resp.json().get("result", [])
                                                                                                    print(f"🆕 دریافت {len(updates)} بروزرسانی جدید")
                                                                                                    for update in updates:
                                                                                                        last_id = update["update_id"]
                                                                                                        with open(STATE_FILE, "w") as f:
                                                                                                            json.dump({"id": last_id}, f)
                                                                                                            msg = update.get("message", {})
                                                                                                            chat_id = msg.get("chat", {}).get("id")
                                                                                                            if not chat_id:
                                                                                                                continue
                                                                                                                # مدیریت پیام متنی ساده
                                                                                                                if "text" in msg:
                                                                                                                    text = msg["text"]
                                                                                                                    if text == "/start":
                                                                                                                        bot.send_message(chat_id, "سلام! ربات فعال شد.")
                                                                                                                    elif text == "/pay":
                                                                                                                        # نمونه پیام درخواست پرداخت (نمایشی)
                                                                                                                        bot.send_message(
                                                                                                                        chat_id, "🚧 پرداخت در دست توسعه است. به زودی فعال میشود."
                                                                                                                        )
                                                                                                                    else:
                                                                                                                        bot.send_message(
                                                                                                                        chat_id, "پیام شما دریافت شد. در حال پردازش..."
                                                                                                                        )
                                                                                                                        # مدیریت عکس یا فایل
                                                                                                                        if "photo" in msg or (
                                                                                                                        "document" in msg
                                                                                                                        and msg.get("document", {}).get("mime_type", "").startswith("image")
                                                                                                                        ):
                                                                                                                            ChaosNeutralizer.atomic_flush(chat_id)
                                                                                                                            try:
                                                                                                                                file_id = msg.get("photo", [{}])[-1].get("file_id") or msg.get(
                                                                                                                                "document", {}
                                                                                                                                ).get("file_id")
                                                                                                                                file_info = bot.session.get(
                                                                                                                                f"{BASE_URL}/getFile",
                                                                                                                                params={"file_id": file_id},
                                                                                                                                timeout=20,
                                                                                                                                ).json()
                                                                                                                                if file_info.get("ok"):
                                                                                                                                    file_path = file_info["result"]["file_path"]
                                                                                                                                    img_url = (
                                                                                                                                    f"https://api.bale.ai/file/bot{API_TOKEN}/{file_path}"
                                                                                                                                    )
                                                                                                                                    local_img = os.path.join(OUTPUT_DIR, f"raw_{chat_id}.jpg")
                                                                                                                                    with open(local_img, "wb") as f_img:
                                                                                                                                        f_img.write(
                                                                                                                                        bot.session.get(img_url, timeout=30).content
                                                                                                                                        )
                                                                                                                                        obj_file = bot.process_with_rhetoric(local_img, chat_id)
                                                                                                                                        if obj_file:
                                                                                                                                            bot.send_file(
                                                                                                                                            chat_id,
                                                                                                                                            obj_file,
                                                                                                                                            caption="✅ استخراج دانش سهبعدی تکمیل شد.",
                                                                                                                                            )
                                                                                                                                            ChaosNeutralizer.atomic_flush(chat_id)
                                                                                                                                        except Exception as e_inner:
                                                                                                                                            print(f"⚠️ اغتشاش درونی مدیریت شد: {e_inner}")
                                                                                                                                        except requests.exceptions.Timeout:
                                                                                                                                            print("⏳ زمان انتظار به پایان رسید. تلاش مجدد...")
                                                                                                                                            time.sleep(2)
                                                                                                                                        except requests.exceptions.ConnectionError as e:
                                                                                                                                            print(f"📡 اختلال در اتصال شبکه: {e}")
                                                                                                                                            time.sleep(10)
                                                                                                                                        except Exception as e:
                                                                                                                                            print(f"❌ خطای پیشبینی نشده: {e}")
                                                                                                                                            time.sleep(5)
                                                                                                                                            if __name__ == "__main__":
                                                                                                                                                main_loop()
