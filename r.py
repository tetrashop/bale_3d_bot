import requests
import time
BT = '659328109:QFVgG7mqkkOFzR_oflqXAb3uEUOXxwIuVVU'
URL = f'https://tapi.bale.ai/bot{BT}'
last_id = 0
print("🚀 بازو آماده است... رامین جان یک پیام در بله بفرست")
while True:
    try:
        response = requests.get(f'{URL}/getUpdates', params={'offset': last_id + 1, 'timeout': 5}).json()
        if 'result' in response:
            for update in response['result']:
                last_id = update['update_id']
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    print(f"📦 در حال ارسال فایل به: {chat_id}")
                    # ارسال فایل STL
                    requests.post(f'{URL}/sendDocument', json={
                    'chat_id': chat_id,
                    'document': 'https://github.com/mrdoob/three.js/raw/master/examples/models/stl/ascii/slotted_disk.stl',
                    'caption': '✅ رامین جان، این هم فایل ۳D شما که منتظرش بودی!'
                    })
                except Exception as e:
                    print(f"Error: {e}")
                    time.sleep(1)
