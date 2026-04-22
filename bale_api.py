import requests
import time
import json
import os
import threading
CACHE_FILE = "update_cache.json"
API_URL = "https://api.bale.ai/bot{token}/"
class BaleAPI:
    def __init__(self, token):
        self.token = token
        self.api_url = API_URL.format(token=token)
        self.update_cache = []
        self.cache_lock = threading.Lock()
        self.load_cache()
        def load_cache(self):
            if os.path.exists(CACHE_FILE):
                try:
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        self.update_cache = json.load(f)
                    except Exception:
                        self.update_cache = []
                    else:
                        self.update_cache = []
                        def save_cache(self):
                            with self.cache_lock:
                                try:
                                    with open(CACHE_FILE, "w", encoding="utf-8") as f:
                                        json.dump(self.update_cache, f, ensure_ascii=False, indent=2)
                                    except Exception:
                                        pass
                                        def get_updates(self, offset=None, timeout=30):
                                            params = {"timeout": timeout}
                                            if offset:
                                                params["offset"] = offset
                                                try:
                                                    response = requests.get(
                                                    self.api_url + "getUpdates", params=params, timeout=timeout + 5
                                                    )
                                                    if response.status_code == 200:
                                                        data = response.json()
                                                        if data.get("ok"):
                                                            updates = data.get("result", [])
                                                            with self.cache_lock:
                                                                # اضافه کردن به کش
                                                                self.update_cache += updates
                                                                # ذخیره کش
                                                                self.save_cache()
                                                                return updates
                                                            else:
                                                                # داده نامعتبر؛ fallback
                                                                return self.load_cached_updates(offset)
                                                            else:
                                                                # خطا؛ fallback
                                                                return self.load_cached_updates(offset)
                                                            except requests.RequestException:
                                                                # اتصال اینترنتی قطع؛ fallback
                                                                return self.load_cached_updates(offset)
                                                                def load_cached_updates(self, offset=None):
                                                                    with self.cache_lock:
                                                                        if offset is None:
                                                                            return self.update_cache.copy()
                                                                        else:
                                                                            return [u for u in self.update_cache if u.get("update_id", 0) >= offset]
                                                                            def send_message(self, chat_id, text):
                                                                                payload = {"chat_id": chat_id, "text": text}
                                                                                try:
                                                                                    response = requests.post(
                                                                                    self.api_url + "sendMessage", json=payload, timeout=10
                                                                                    )
                                                                                    if response.status_code == 200:
                                                                                        return True
                                                                                    else:
                                                                                        # ذخیره پیام برای ارسال بعدی
                                                                                        self.queue_offline_message(payload)
                                                                                        return False
                                                                                    except requests.RequestException:
                                                                                        self.queue_offline_message(payload)
                                                                                        return False
                                                                                        OFFLINE_MESSAGES_FILE = "offline_messages.json"
                                                                                        offline_messages_lock = threading.Lock()
                                                                                        def queue_offline_message(self, payload):
                                                                                            with self.offline_messages_lock:
                                                                                                messages = []
                                                                                                if os.path.exists(self.OFFLINE_MESSAGES_FILE):
                                                                                                    try:
                                                                                                        with open(self.OFFLINE_MESSAGES_FILE, "r", encoding="utf-8") as f:
                                                                                                            messages = json.load(f)
                                                                                                        except Exception:
                                                                                                            messages = []
                                                                                                            messages.append(payload)
                                                                                                            try:
                                                                                                                with open(self.OFFLINE_MESSAGES_FILE, "w", encoding="utf-8") as f:
                                                                                                                    json.dump(messages, f, ensure_ascii=False, indent=2)
                                                                                                                except Exception:
                                                                                                                    pass
                                                                                                                    def retry_offline_messages(self):
                                                                                                                        with self.offline_messages_lock:
                                                                                                                            if not os.path.exists(self.OFFLINE_MESSAGES_FILE):
                                                                                                                                return
                                                                                                                                try:
                                                                                                                                    with open(self.OFFLINE_MESSAGES_FILE, "r", encoding="utf-8") as f:
                                                                                                                                        messages = json.load(f)
                                                                                                                                    except Exception:
                                                                                                                                        return
                                                                                                                                        remain = []
                                                                                                                                        for payload in messages:
                                                                                                                                            try:
                                                                                                                                                response = requests.post(
                                                                                                                                                self.api_url + "sendMessage", json=payload, timeout=10
                                                                                                                                                )
                                                                                                                                                if response.status_code != 200:
                                                                                                                                                    remain.append(payload)
                                                                                                                                                except requests.RequestException:
                                                                                                                                                    remain.append(payload)
                                                                                                                                                    try:
                                                                                                                                                        if remain:
                                                                                                                                                            with open(self.OFFLINE_MESSAGES_FILE, "w", encoding="utf-8") as f:
                                                                                                                                                                json.dump(remain, f, ensure_ascii=False, indent=2)
                                                                                                                                                            else:
                                                                                                                                                                os.remove(self.OFFLINE_MESSAGES_FILE)
                                                                                                                                                            except Exception:
                                                                                                                                                                pass
                                                                                                                                                                def poll_updates_loop(self, handler_func, polling_interval=3):
                                                                                                                                                                    last_update_id = None
                                                                                                                                                                    while True:
                                                                                                                                                                        updates = self.get_updates(
                                                                                                                                                                        offset=last_update_id + 1 if last_update_id else None, timeout=30
                                                                                                                                                                        )
                                                                                                                                                                        if updates:
                                                                                                                                                                            for u in updates:
                                                                                                                                                                                handler_func(u)
                                                                                                                                                                                last_update_id = updates[-1]["update_id"]
                                                                                                                                                                                # تلاش برای ارسال پیامهای آفلاین
                                                                                                                                                                                self.retry_offline_messages()
                                                                                                                                                                                time.sleep(polling_interval)
