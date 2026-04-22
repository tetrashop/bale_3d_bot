import os
import time
import requests
from error_handler import ErrorHandler, logger
from revenue_manager import RevenueManager
from payment_manager import PaymentManager
from knowledge_extractor import KnowledgeExtractor
from engine_3d import Engine3D
from utils import download_file

BASE_DIR = os.getenv("BASE_DIR", ".")
OFFLINE_INPUT_DIR = os.path.join(BASE_DIR, "offline_inputs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OFFLINE_INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class BaleBotAtena:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({"Connection": "keep-alive"})
        self.states = {}
        self.revenue = RevenueManager()
        self.payment = PaymentManager()
        self.engine = Engine3D()
        self.knowledge = KnowledgeExtractor()
        self.error_handler = ErrorHandler()

    def send_message(self, chat_id, text, keyboard=None):
        url = f"https://api.bale.ai/bot{self.api_token}/message/send"
        data = {
            "receiver": str(chat_id),
            "type": "text",
            "content": {"text": text}
        }
        if keyboard:
            data["keyboard"] = keyboard
        try:
            resp = self.session.post(url, json=data, timeout=20)
            resp.raise_for_status()
            logger.info(f"Sent message to {chat_id}")
        except Exception as e:
            logger.error(f"send_message error: {e}")

    def send_file(self, chat_id, file_path, caption=None):
        url = f"https://api.bale.ai/bot{self.api_token}/file/upload"
        try:
            with open(file_path, "rb") as f:
                data = {"receiver": str(chat_id)}
                if caption:
                    data["caption"] = caption
                resp = self.session.post(url, data=data, files={"file": f}, timeout=60)
                resp.raise_for_status()
                logger.info(f"Sent file {file_path} to {chat_id}")
        except Exception as e:
            logger.error(f"send_file error: {e}")

    def set_state(self, chat_id, state):
        self.states[chat_id] = state

    def get_state(self, chat_id):
        return self.states.get(chat_id, "MAIN_MENU")

    def handle_update(self, update):
        try:
            message = update.get("message")
            if message:
                chat_id = message.get("chat", {}).get("id")
                if not chat_id:
                    return
                text = (message.get("text") or "").strip()
                photo = message.get("photo")
                video = message.get("video")
                document = message.get("document")
                state = self.get_state(chat_id)

                if text == "/start":
                    self.set_state(chat_id, "MAIN_MENU")
                    keyboard = {
                        "type": "keyboard",
                        "buttons": [
                            [{"type": "text", "title": "ساخت مدل سهبعدی"}],
                            [{"type": "text", "title": "وضعیت حساب"}],
                            [{"type": "text", "title": "شارژ حساب"}],
                            [{"type": "text", "title": "استخراج دانش"}],
                            [{"type": "text", "title": "راهنما"}]
                        ]
                    }
                    self.send_message(chat_id, "سلام! چگونه میتوانم کمک کنم؟", keyboard)
                    return

                if state == "MAIN_MENU":
                    if text == "ساخت مدل سهبعدی":
                        self.set_state(chat_id, "WAITING_FOR_MEDIA")
                        self.send_message(chat_id, "لطفا تصویر یا ویدیوی خود را ارسال کنید.")
                        return
                    elif text == "وضعیت حساب":
                        bal = self.revenue.get_balance(chat_id)
                        self.send_message(chat_id, f"موجودی شما: {bal} واحد")
                        return
                    elif text == "شارژ حساب":
                        keyboard = {
                            "type": "inline_keyboard",
                            "buttons": [
                                [{"text": "شارژ ۵ واحد", "callback_data": "pay_5"}],
                                [{"text": "شارژ ۱۰ واحد", "callback_data": "pay_10"}]
                            ]
                        }
                        self.send_message(chat_id, "برای شارژ حساب یکی از مقادیر را انتخاب کنید:", keyboard)
                        return
                    elif text == "استخراج دانش":
                        self.set_state(chat_id, "WAITING_FOR_KNOWLEDGE")
                        self.send_message(chat_id, "لطفا متن مورد نظر برای استخراج دانش را ارسال کنید.")
                        return
                    elif text == "راهنما":
                        self.send_message(chat_id,
                            "با انتخاب 'ساخت مدل سهبعدی' عکس یا ویدیو ارسال کنید.\n"
                            "برای شارژ حساب 'شارژ حساب' را انتخاب کنید.\n"
                            "برای استخراج دانش، 'استخراج دانش' را انتخاب کنید."
                        )
                        return
                    else:
                        self.send_message(chat_id, "لطفا یکی از گزینه های منو را انتخاب کنید.")
                        return

                if state == "WAITING_FOR_KNOWLEDGE":
                    self.knowledge.extract({f"user_{chat_id}_input": text})
                    self.send_message(chat_id, "دانش شما ذخیره شد. میتوانید متن بیشتری ارسال کنید یا به منوی اصلی بازگردید.")
                    return

                if state == "WAITING_FOR_MEDIA":
                    if photo:
                        file_id = photo[-1].get("file_id")
                        local_path = os.path.join(OFFLINE_INPUT_DIR, f"photo_{chat_id}_{int(time.time())}.jpg")
                        if download_file(self.session, file_id, local_path):
                            obj_filename = os.path.join(OUTPUT_DIR, f"model_{chat_id}_{int(time.time())}.obj")
                            success, result = self.engine.generate_model_offline(local_path, obj_filename)
                            if success:
                                cost = 1
                                if self.revenue.decrease_balance(chat_id, cost):
                                    self.send_file(chat_id, result, caption="مدل سهبعدی شما")
                                else:
                                    self.send_message(chat_id, "موجودی شما کافی نیست، لطفاً ابتدا شارژ کنید.")
                            else:
                                self.send_message(chat_id, f"خطا در ساخت مدل: {result}")
                        else:
                            self.send_message(chat_id, "خطا در دریافت تصویر.")
                        self.set_state(chat_id, "MAIN_MENU")
                        return

                    if video:
                        file_id = video.get("file_id")
                        local_path = os.path.join(OFFLINE_INPUT_DIR, f"video_{chat_id}_{int(time.time())}.mp4")
                        if download_file(self.session, file_id, local_path):
                            model_data = self.engine.process_video_to_3d(local_path)
                            if model_data:
                                obj_path = os.path.join(OUTPUT_DIR, f"model_{chat_id}_{int(time.time())}.obj")
                                with open(obj_path, "wb") as f:
                                    f.write(model_data)
                                cost = 2
                                if self.revenue.decrease_balance(chat_id, cost):
                                    self.send_file(chat_id, obj_path, caption="مدل سهبعدی ساخته شده از ویدیو")
                                else:
                                    self.send_message(chat_id, "موجودی کافی برای ساخت مدل ویدیویی ندارید.")
                            else:
                                self.send_message(chat_id, "خطا در ساخت مدل از ویدیو.")
                        else:
                            self.send_message(chat_id, "خطا در دریافت ویدیو.")
                        self.set_state(chat_id, "MAIN_MENU")
                        return

                    if document and document.get("file_name", "").lower().endswith((".mp4", ".avi", ".mov")):
                        file_id = document.get("file_id")
                        fname = document.get("file_name")
                        local_path = os.path.join(OFFLINE_INPUT_DIR, f"video_{chat_id}_{int(time.time())}_{fname}")
                        if download_file(self.session, file_id, local_path):
                            model_data = self.engine.process_video_to_3d(local_path)
                            if model_data:
                                obj_path = os.path.join(OUTPUT_DIR, f"model_{chat_id}_{int(time.time())}.obj")
                                with open(obj_path, "wb") as f:
                                    f.write(model_data)
                                cost = 2
                                if self.revenue.decrease_balance(chat_id, cost):
                                    self.send_file(chat_id, obj_path, caption="مدل سهبعدی از فایل ویدیویی")
                                else:
                                    self.send_message(chat_id, "موجودی کافی برای ساخت مدل ویدیویی ندارید.")
                            else:
                                self.send_message(chat_id, "خطا در ساخت مدل از ویدیو.")
                        else:
                            self.send_message(chat_id, "خطا در دریافت فایل ویدیویی.")
                        self.set_state(chat_id, "MAIN_MENU")
                        return

                    self.send_message(chat_id, "لطفا یک تصویر یا ویدیو معتبر ارسال کنید.")
                    return

            callback = update.get("callback_query")
            if callback:
                data = callback.get("data", "")
                from_user = callback.get("from", {})
                c_id = from_user.get("id")
                if data.startswith("pay_"):
                    amount = int(data.split("_")[1])
                    pay_id = self.payment.record_payment(amount)
                    if pay_id:
                        self.revenue.increase_balance(c_id, amount)
                        self.send_message(c_id, f"حساب شما با مقدار {amount} واحد شارژ شد. ممنون از شما!")
                    else:
                        self.send_message(c_id, "خطا در ثبت پرداخت. لطفا دوباره تلاش کنید.")
                    return
        except Exception as e:
            logger.error(f"Exception in handle_update: {e}", exc_info=True)
            try:
                if "chat_id" in locals():
                    self.send_message(chat_id, "خطایی رخ داد، لطفا دوباره تلاش کنید.")
            except Exception:
                pass
