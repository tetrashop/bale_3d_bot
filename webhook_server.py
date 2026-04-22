from flask import Flask, request, jsonify
from bale_bot_atena import BaleBotAtena

app = Flask(__name__)
bot = BaleBotAtena("YOUR_API_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    bot.handle_update(update)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
