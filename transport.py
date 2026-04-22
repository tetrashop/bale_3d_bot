import os
import requests
from config import BOT_TOKEN
def _get_send_method(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return "sendPhoto"
    elif ext in [".mp4", ".mkv", ".avi", ".mov"]:
        return "sendVideo"
    else:
        return "sendDocument"
        def send_file_to_user(user_id, file_path):
            if not BOT_TOKEN:
                raise RuntimeError("BOT_TOKEN is not set")
                if not os.path.isfile(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                    method = _get_send_method(file_path)
                    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/{method}"
                    data = {"user_id": str(user_id)}
                    headers = {"Authorization": f"Bearer {BOT_TOKEN}"}
                    with open(file_path, "rb") as f:
                        files = {"file": f}
                        resp = requests.post(url, data=data, files=files, headers=headers, timeout=120)
                        resp.raise_for_status()
                        print(f"[SEND] method={method} file={file_path} to user_id={user_id}", flush=True)
                        return resp.json() if resp.content else {"ok": True}
