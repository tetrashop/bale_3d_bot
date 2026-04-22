import os
import time
import json
import shutil
import subprocess
import requests
from config import (
BOT_TOKEN,
BASE_URL,
DOWNLOAD_DIR,
OUTPUT_DIR,
PAYMENT_MODE,
PAYMENT_URL_TEST,
PAYMENT_URL_LIVE,
PRICE_TOMAN,
THREE_D_ENGINE_PATH,
DEFAULT_OUTPUT_EXT,
HTTP_TIMEOUT,
UPLOAD_TIMEOUT,
)
USERS_FILE = "users.json"
PENDING_FILE = "pending.json"
def load_json(path, default):
    if not os.path.exists(path):
        return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
            except Exception:
                return default
                def save_json(path, data):
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        def ensure_dirs():
                            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                            os.makedirs(OUTPUT_DIR, exist_ok=True)
                            def send_message(chat_id, text):
                                try:
                                    requests.post(
                                    f"{BASE_URL}/sendMessage",
                                    json={"chat_id": chat_id, "text": text},
                                    timeout=HTTP_TIMEOUT,
                                    )
                                except Exception as e:
                                    print("send_message error:", e)
                                    def send_file(chat_id, file_path, caption=""):
                                        try:
                                            with open(file_path, "rb") as f:
                                                files = {"document": f}
                                                data = {"chat_id": chat_id, "caption": caption}
                                                requests.post(
                                                f"{BASE_URL}/sendDocument",
                                                data=data,
                                                files=files,
                                                timeout=UPLOAD_TIMEOUT,
                                                )
                                            except Exception as e:
                                                print("send_file error:", e)
                                                def get_file_path_from_bale(file_id):
                                                    try:
                                                        resp = requests.get(
                                                        f"{BASE_URL}/getFile", params={"file_id": file_id}, timeout=HTTP_TIMEOUT
                                                        ).json()
                                                        if not resp.get("ok"):
                                                            return None
                                                            return resp["result"]["file_path"]
                                                        except Exception as e:
                                                            print("get_file_path_from_bale error:", e)
                                                            return None
                                                            def download_bale_file(file_id, local_name):
                                                                try:
                                                                    file_path = get_file_path_from_bale(file_id)
                                                                    if not file_path:
                                                                        return None
                                                                        dl_url = f"https://tapi.bale.ai/file/bot{BOT_TOKEN}/{file_path}"
                                                                        r = requests.get(dl_url, timeout=UPLOAD_TIMEOUT)
                                                                        r.raise_for_status()
                                                                        ensure_dirs()
                                                                        full_path = os.path.join(DOWNLOAD_DIR, local_name)
                                                                        with open(full_path, "wb") as f:
                                                                            f.write(r.content)
                                                                            return full_path
                                                                        except Exception as e:
                                                                            print("download_bale_file error:", e)
                                                                            return None
                                                                            def get_payment_link():
                                                                                if PAYMENT_MODE == "live":
                                                                                    return PAYMENT_URL_LIVE
                                                                                    return PAYMENT_URL_TEST
                                                                                    def build_menu_text():
                                                                                        payment_text = "آزمایشی" if PAYMENT_MODE == "test" else "واقعی"
                                                                                        return (
                                                                                        "سلام! به ربات تبدیل فایل به سهبعدی خوش آمدی."
                                                                                        f"قیمت تبدیل: {PRICE_TOMAN:,} تومان"
                                                                                        f"وضعیت پرداخت: {payment_text}"
                                                                                        "دستورات:"
                                                                                        "/start - شروع"
                                                                                        "/price - قیمت"
                                                                                        "/buy - خرید/پرداخت"
                                                                                        "/paid - تایید پرداخت (فقط test)"
                                                                                        "بعد از پرداخت، فایل یا عکس را بفرست."
                                                                                        )
                                                                                        def convert_to_3d(input_path, output_name):
                                                                                            ensure_dirs()
                                                                                            output_path = os.path.join(OUTPUT_DIR, output_name)
                                                                                            if THREE_D_ENGINE_PATH and os.path.exists(THREE_D_ENGINE_PATH):
                                                                                                try:
                                                                                                    result = subprocess.run(
                                                                                                    ["python3", THREE_D_ENGINE_PATH, input_path, output_path],
                                                                                                    capture_output=True,
                                                                                                    text=True,
                                                                                                    timeout=300,
                                                                                                    )
                                                                                                    if result.returncode != 0:
                                                                                                        print("3D engine stderr:", result.stderr)
                                                                                                        raise RuntimeError("3D engine failed")
                                                                                                        if not os.path.exists(output_path):
                                                                                                            raise FileNotFoundError("3D output was not created")
                                                                                                            return output_path
                                                                                                        except Exception as e:
                                                                                                            print("convert_to_3d external error:", e)
                                                                                                            raise
                                                                                                            shutil.copy2(input_path, output_path)
                                                                                                            return output_path
                                                                                                            def process_pending(chat_id, source_path):
                                                                                                                try:
                                                                                                                    send_message(chat_id, "پردازش شروع شد... لطفاً صبر کن.")
                                                                                                                    base_name = f"3d_{int(time.time())}"
                                                                                                                    output_name = base_name + DEFAULT_OUTPUT_EXT
                                                                                                                    output_path = convert_to_3d(source_path, output_name)
                                                                                                                    send_file(chat_id, output_path, "✅ فایل خروجی آماده است.")
                                                                                                                    send_message(chat_id, "فایل با موفقیت تحویل داده شد.")
                                                                                                                except Exception as e:
                                                                                                                    print("process_pending error:", e)
                                                                                                                    send_message(chat_id, "❌ خطا در پردازش فایل رخ داد.")
                                                                                                                    def mark_paid(chat_id, users):
                                                                                                                        users[chat_id]["paid"] = True
                                                                                                                        save_json(USERS_FILE, users)
                                                                                                                        def main():
                                                                                                                            ensure_dirs()
                                                                                                                            users = load_json(USERS_FILE, {})
                                                                                                                            pending_files = load_json(PENDING_FILE, {})
                                                                                                                            last_id = 0
                                                                                                                            print("ربات روشن شد...")
                                                                                                                            while True:
                                                                                                                                try:
                                                                                                                                    resp = requests.get(
                                                                                                                                    f"{BASE_URL}/getUpdates",
                                                                                                                                    params={"offset": last_id + 1, "timeout": 10},
                                                                                                                                    timeout=20,
                                                                                                                                    ).json()
                                                                                                                                    for up in resp.get("result", []):
                                                                                                                                        update_id = up.get("update_id")
                                                                                                                                        if update_id is None:
                                                                                                                                            continue
                                                                                                                                            last_id = update_id
                                                                                                                                            msg = up.get("message", {})
                                                                                                                                            chat = msg.get("chat", {})
                                                                                                                                            chat_id = str(chat.get("id"))
                                                                                                                                            text = msg.get("text", "")
                                                                                                                                            if not chat_id:
                                                                                                                                                continue
                                                                                                                                                if chat_id not in users:
                                                                                                                                                    users[chat_id] = {"paid": False, "created_at": int(time.time())}
                                                                                                                                                    save_json(USERS_FILE, users)
                                                                                                                                                    if text == "/start":
                                                                                                                                                        send_message(chat_id, build_menu_text())
                                                                                                                                                    elif text == "/price":
                                                                                                                                                        send_message(chat_id, f"هزینه تبدیل سهبعدی: {PRICE_TOMAN:,} تومان")
                                                                                                                                                    elif text == "/buy":
                                                                                                                                                        pay_link = get_payment_link()
                                                                                                                                                        if PAYMENT_MODE == "test":
                                                                                                                                                            send_message(
                                                                                                                                                            chat_id,
                                                                                                                                                            "پرداخت آزمایشی فعال است."
                                                                                                                                                            f"لینک تست:{pay_link}"
                                                                                                                                                            "بعد از انجام تست، /paid را بفرست.",
                                                                                                                                                            )
                                                                                                                                                        else:
                                                                                                                                                            send_message(
                                                                                                                                                            chat_id,
                                                                                                                                                            "پرداخت واقعی فعال است."
                                                                                                                                                            f"لینک پرداخت:{pay_link}"
                                                                                                                                                            "بعد از پرداخت واقعی، باید verify درگاه را وصل کنی.",
                                                                                                                                                            )
                                                                                                                                                        elif text == "/paid":
                                                                                                                                                            if PAYMENT_MODE == "test":
                                                                                                                                                                mark_paid(chat_id, users)
                                                                                                                                                                if chat_id in pending_files:
                                                                                                                                                                    source_path = pending_files[chat_id]
                                                                                                                                                                    process_pending(chat_id, source_path)
                                                                                                                                                                    del pending_files[chat_id]
                                                                                                                                                                    save_json(PENDING_FILE, pending_files)
                                                                                                                                                                else:
                                                                                                                                                                    send_message(
                                                                                                                                                                    chat_id,
                                                                                                                                                                    "فعلاً فایلی ثبت نشده است. اول فایل یا عکس را بفرست.",
                                                                                                                                                                    )
                                                                                                                                                                else:
                                                                                                                                                                    send_message(
                                                                                                                                                                    chat_id,
                                                                                                                                                                    "در حالت واقعی، تایید پرداخت باید از verify درگاه انجام شود، نه /paid.",
                                                                                                                                                                    )
                                                                                                                                                                elif "document" in msg:
                                                                                                                                                                    doc = msg["document"]
                                                                                                                                                                    file_id = doc["file_id"]
                                                                                                                                                                    file_name = doc.get("file_name", f"{int(time.time())}.bin")
                                                                                                                                                                    send_message(chat_id, "در حال دریافت فایل...")
                                                                                                                                                                    path = download_bale_file(file_id, file_name)
                                                                                                                                                                    if path:
                                                                                                                                                                        pending_files[chat_id] = path
                                                                                                                                                                        save_json(PENDING_FILE, pending_files)
                                                                                                                                                                        if users[chat_id].get("paid"):
                                                                                                                                                                            send_message(
                                                                                                                                                                            chat_id, "پرداخت تایید شده. تبدیل شروع میشود..."
                                                                                                                                                                            )
                                                                                                                                                                            process_pending(chat_id, path)
                                                                                                                                                                            if chat_id in pending_files:
                                                                                                                                                                                del pending_files[chat_id]
                                                                                                                                                                                save_json(PENDING_FILE, pending_files)
                                                                                                                                                                            else:
                                                                                                                                                                                send_message(
                                                                                                                                                                                chat_id,
                                                                                                                                                                                f"✅ فایل دریافت شد."
                                                                                                                                                                                f"برای شروع تبدیل، لطفاً {PRICE_TOMAN:,} تومان پرداخت کن و سپس /paid را بفرست.",
                                                                                                                                                                                )
                                                                                                                                                                            else:
                                                                                                                                                                                send_message(chat_id, "❌ دانلود فایل ناموفق بود.")
                                                                                                                                                                            elif "photo" in msg:
                                                                                                                                                                                photo = msg["photo"][-1]
                                                                                                                                                                                file_id = photo["file_id"]
                                                                                                                                                                                file_name = f"{int(time.time())}.jpg"
                                                                                                                                                                                send_message(chat_id, "در حال دریافت عکس...")
                                                                                                                                                                                path = download_bale_file(file_id, file_name)
                                                                                                                                                                                if path:
                                                                                                                                                                                    pending_files[chat_id] = path
                                                                                                                                                                                    save_json(PENDING_FILE, pending_files)
                                                                                                                                                                                    if users[chat_id].get("paid"):
                                                                                                                                                                                        send_message(
                                                                                                                                                                                        chat_id, "پرداخت تایید شده. تبدیل شروع میشود..."
                                                                                                                                                                                        )
                                                                                                                                                                                        process_pending(chat_id, path)
                                                                                                                                                                                        if chat_id in pending_files:
                                                                                                                                                                                            del pending_files[chat_id]
                                                                                                                                                                                            save_json(PENDING_FILE, pending_files)
                                                                                                                                                                                        else:
                                                                                                                                                                                            send_message(
                                                                                                                                                                                            chat_id,
                                                                                                                                                                                            f"✅ عکس دریافت شد."
                                                                                                                                                                                            f"برای شروع تبدیل، لطفاً {PRICE_TOMAN:,} تومان پرداخت کن و سپس /paid را بفرست.",
                                                                                                                                                                                            )
                                                                                                                                                                                        else:
                                                                                                                                                                                            send_message(chat_id, "❌ دانلود عکس ناموفق بود.")
                                                                                                                                                                                        except Exception as e:
                                                                                                                                                                                            print("main error:", e)
                                                                                                                                                                                            time.sleep(1)
                                                                                                                                                                                            if __name__ == "__main__":
                                                                                                                                                                                                main()
