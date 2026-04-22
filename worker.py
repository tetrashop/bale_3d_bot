import threading
import queue
import logging
import numpy as np
import asyncio
import threading
import queue
from engine_3d import generate_model_offline
logger = logging.getLogger("worker")
logging.basicConfig(level=logging.INFO)
job_queue = queue.Queue()
def worker_thread():
    while True:
        job = job_queue.get()
        if job is None:
            break
            chat_id, image_path, output_path, callback = job
            success = generate_model_offline(image_path, output_path)
            callback(chat_id, output_path if success else None)
            job_queue.task_done()
            worker = threading.Thread(target=worker_thread, daemon=True)
            worker.start()
            def add_job(chat_id: int, image_path: str, output_path: str, callback):
                job_queue.put((chat_id, image_path, output_path, callback))
                def generate_model_offline(image_data):
                    try:
                        if not isinstance(image_data, np.ndarray):
                            raise TypeError("Input must be numpy ndarray")
                            if image_data.ndim != 2:
                                raise ValueError("Input must be 2D array")
                                rows, cols = image_data.shape
                                normalized = image_data / 255.0
                                vertices = []
                                for i in range(rows):
                                    for j in range(cols):
                                        vertices.append((float(j), float(i), float(normalized[i, j])))
                                        faces = []
                                        for i in range(rows - 1):
                                            for j in range(cols - 1):
                                                tl = i * cols + j
                                                tr = tl + 1
                                                bl = (i + 1) * cols + j
                                                br = bl + 1
                                                faces.append((tl, bl, tr))
                                                faces.append((tr, bl, br))
                                                model = {"vertices": vertices, "faces": faces}
                                                return True, model
                                            except Exception as e:
                                                logger.error(f"Error generating 3D model: {e}", exc_info=True)
                                                return False, str(e)
                                                async def send_message(chat_id: str, text: str, send_func):
                                                    try:
                                                        await send_func(chat_id, text)
                                                    except Exception as e:
                                                        logger.error(f"Error sending message: {e}")
                                                        def download_image(url: str):
                                                            try:
                                                                import requests
                                                                r = requests.get(url, timeout=5)
                                                                r.raise_for_status()
                                                                import cv2
                                                                data = np.frombuffer(r.content, np.uint8)
                                                                img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
                                                                if img is None:
                                                                    logger.warning("opencv failed to decode image")
                                                                    return img
                                                                except Exception as e:
                                                                    logger.warning(f"Image download failed: {e}")
                                                                    return None
                                                                    def worker_loop(send_func):
                                                                        while True:
                                                                            job = job_queue.get()
                                                                            if job is None:
                                                                                job_queue.task_done()
                                                                                break
                                                                                chat_id = job.get("chatId")
                                                                                image_url = job.get("imageUrl")
                                                                                try:
                                                                                    img = None
                                                                                    if image_url:
                                                                                        img = download_image(image_url)
                                                                                        if img is None:
                                                                                            asyncio.run(
                                                                                            send_message(
                                                                                            chat_id,
                                                                                            "خطا: امکان دریافت تصویر به دلیل قطعی اینترنت وجود ندارد. لطفا تصویر را در فرمت پایه (base64 یا فایل) ارسال کنید.",
                                                                                            send_func,
                                                                                            )
                                                                                            )
                                                                                            job_queue.task_done()
                                                                                            continue
                                                                                            success, model_or_err = generate_model_offline(img)
                                                                                            if success:
                                                                                                text_resp = f"مدل ۳بعدی ساخته شد.\nتعداد رئوس: {len(model_or_err['vertices'])}\nتعداد وجهها: {len(model_or_err['faces'])}"
                                                                                            else:
                                                                                                text_resp = f"خطا در ساخت مدل: {model_or_err}"
                                                                                                asyncio.run(send_message(chat_id, text_resp, send_func))
                                                                                            except Exception as e:
                                                                                                logger.error(f"Error processing job for chat {chat_id}: {e}", exc_info=True)
                                                                                                asyncio.run(send_message(chat_id, "خطای داخلی در پردازش مدل.", send_func))
                                                                                            finally:
                                                                                                job_queue.task_done()
                                                                                                def start_worker(send_func):
                                                                                                    t = threading.Thread(target=worker_loop, args=(send_func,), daemon=True)
                                                                                                    t.start()
                                                                                                    return t
                                                                                                    def stop_worker():
                                                                                                        job_queue.put(None)
