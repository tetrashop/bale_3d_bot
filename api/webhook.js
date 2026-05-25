const axios = require('axios');

const BOT_TOKEN = process.env.BOT_TOKEN;
if (!BOT_TOKEN) {
  console.error("FATAL: BOT_TOKEN environment variable is not set.");
}

const BALE_API_URL = `https://tapi.bale.ai/bot${BOT_TOKEN}`;

async function callBaleApi(method, params) {
  try {
    const response = await axios.post(`${BALE_API_URL}/${method}`, params);
    return response.data;
  } catch (error) {
    console.error(`Error calling Bale API method ${method}:`, error.response?.data || error.message);
    return null;
  }
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const update = req.body;
  console.log("Received update:", JSON.stringify(update));

  res.status(200).send('OK');

  try {
    if (!update.message) return;

    const message = update.message;
    const chatId = message.chat.id;

    if (message.text === '/start') {
      await callBaleApi('sendMessage', {
        chat_id: chatId,
        text: "سلام! من ربات تبدیل 2D به 3D هستم. یک عکس برای من بفرستید."
      });
    } else if (message.photo) {
      await callBaleApi('sendMessage', {
        chat_id: chatId,
        text: "عکس شما دریافت شد. در حال پردازش..."
      });
    } else {
      await callBaleApi('sendMessage', {
        chat_id: chatId,
        text: "لطفا یک عکس برای من بفرستید یا از دستور /start استفاده کنید."
      });
    }
  } catch (error) {
    console.error("Error processing update:", error);
  }
};
