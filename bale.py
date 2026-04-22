from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np
import threading
import queue
import logging
import httpx
app = FastAPI()
logger = logging.getLogger("bale_2dto3d")
logging.basicConfig(level=logging.INFO)
job_queue = queue.Queue()
BALE_BOT_TOKEN = "YOUR_BALE_BOT_TOKEN"
BALE_API_URL = f"https://edge.bale.ai/bot{BALE_BOT_TOKEN}"
class BaleMessage(BaseModel):
    chatId: str
    type: str  # "text" or "image"
    content: dict
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
                                    async def send_message(chat_id: str, text: str):
                                        async with httpx.AsyncClient() as client:
                                            payload = {"receiver": chat_id, "type": "text", "content": {"text": text}}
                                            r = await client.post(f"{BALE_API_URL}/message/send", json=payload)
                                            if r.status_code != 200:
                                                logger.error(f"Failed sending message: {r.text}")
                                                def download_image(url: str) -> np.ndarray:
                                                    import requests
                                                    r = requests.get(url)
                                                    if r.status_code == 200:
                                                        data = np.frombuffer(r.content, np.uint8)
                                                        import cv2
                                                        img = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
                                                        return img
                                                        return None
                                                        def worker_loop():
                                                            while True:
                                                                job = job_queue.get()
                                                                if job is None:
                                                                    job_queue.task_done()
                                                                    break
                                                                    chat_id = job["chatId"]
                                                                    image_url = job["imageUrl"]
                                                                    try:
                                                                        img = download_image(image_url)
                                                                        if img is None:
                                                                            import asyncio
                                                                            asyncio.run(send_message(chat_id, "خطا در دریافت تصویر."))
                                                                            job_queue.task_done()
                                                                            continue
                                                                            success, model_or_err = generate_model_offline(img)
                                                                            if success:
                                                                                text_resp = f"مدل ۳بعدی ساخته شد.\nتعداد رئوس: {len(model_or_err['vertices'])}\nتعداد وجهها: {len(model_or_err['faces'])}"
                                                                            else:
                                                                                text_resp = f"خطا در ساخت مدل: {model_or_err}"
                                                                                asyncio.run(send_message(chat_id, text_resp))
                                                                            except Exception as e:
                                                                                logger.error(f"Error processing job for chat {chat_id}: {e}", exc_info=True)
                                                                                asyncio.run(send_message(chat_id, "خطای داخلی در پردازش مدل."))
                                                                            finally:
                                                                                job_queue.task_done()
                                                                                worker_thread = threading.Thread(target=worker_loop, daemon=True)
                                                                                worker_thread.start()
                                                                                @app.post("/webhook")
                                                                                async def webhook_handler(update: dict):
                                                                                    try:
                                                                                        msg = update.get("message", {})
                                                                                        chat_id = msg.get("chatId")
                                                                                        msg_type = msg.get("type")
                                                                                        if not chat_id or not msg_type:
                                                                                            return {"status": "ignored"}
                                                                                            if msg_type == "image":
                                                                                                image_url = msg.get("content", {}).get("url")
                                                                                                if image_url is None:
                                                                                                    return {"status": "no_url"}
                                                                                                    job_queue.put({"chatId": chat_id, "imageUrl": image_url})
                                                                                                    await send_message(
                                                                                                    chat_id, "تصویر دریافت شد و در صف پردازش قرار گرفت. لطفا منتظر بمانید."
                                                                                                    )
                                                                                                else:
                                                                                                    await send_message(chat_id, "لطفا فقط تصویر ارسال کنید تا مدل ۳بعدی بسازم.")
                                                                                                    return {"status": "ok"}
                                                                                                except Exception as e:
                                                                                                    logger.error(f"Error in webhook handler: {e}", exc_info=True)
                                                                                                    return {"status": "error"}
                                                                                                    # اگر نیاز به خروج منظم بود، میتوان stop_worker را صدا زد.
