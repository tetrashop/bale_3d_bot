import json
from bale_bot_atena import handle_update  # اگر handle_update تعریف شده در این فایل
def handler(request, response):
    if request.method != "POST":
        return response.status(405).send("Method Not Allowed")
        update = request.json
        try:
            handle_update(update)
        except Exception as e:
            print(f"Error: {e}")
            return response.send({"status": "ok"})
            def handle_update(update):
                message = update.get("message")
                if not message:
                    return
                    user_id = message["from"]["id"]
                    text = message.get("text", "")
                    if text == "/reset":
                        clear_user_data(user_id)
                        send_message(user_id, "ربات با موفقیت ریست شد.")
                        return
                        # کدهای دیگر پردازش پیام
                        def clear_user_data(user_id):
                            # پاکسازی دادهها مثل دیتابیس یا کش مرتبط با user_id
                            pass
                            def send_message(user_id, text):
                                # ارسال پیام به کاربر از طریق API بله
                                pass
