import threading
import time
import logging
import queue
class RescueSystem:
    def __init__(self, bale_api):
        self.bale_api = bale_api
        self.logger = logging.getLogger("RescueSystem")
        self.message_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        def _worker_loop(self):
            backoff = 1
            while not self.stop_event.is_set():
                try:
                    message = self.message_queue.get(timeout=1)
                except queue.Empty:
                    time.sleep(0.1)
                    continue
                    chat_id, text = message
                    success = self.bale_api.send_message(chat_id, text)
                    if not success:
                        # وقتی ارسال پیام ناموفق است پیام را دوباره صفبندی کن
                        self.logger.warning(
                        f"Send failed. Re-queue message to chat_id {chat_id}"
                        )
                        self.message_queue.put((chat_id, text))
                        time.sleep(backoff)
                        backoff = min(backoff * 2, 30)  # اکسپوننشیال بکآف تا ۳۰ ثانیه
                    else:
                        backoff = 1
                        def enqueue_message(self, chat_id, text):
                            self.logger.info(f"Enqueue message to chat_id {chat_id}")
                            self.message_queue.put((chat_id, text))
                            def stop(self):
                                self.stop_event.set()
                                self.worker_thread.join()
                                def run_fallback_check_loop(self, interval=60):
                                    """
                                    به صورت دورهای تلاش میکند پیامهای آفلاین ذخیره شده در bale_api را ارسال کند.
                                    """
                                    while not self.stop_event.is_set():
                                        try:
                                            self.logger.info("Attempting to flush offline messages...")
                                            self.bale_api.retry_offline_messages()
                                        except Exception as e:
                                            self.logger.error(f"Error during offline message retry: {e}")
                                            time.sleep(interval)
