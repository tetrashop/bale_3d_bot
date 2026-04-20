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
