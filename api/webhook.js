module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).send('Method Not Allowed');
  }
  const BOT_TOKEN = process.env.BOT_TOKEN;
  if (!BOT_TOKEN) {
    console.error('BOT_TOKEN missing');
    return res.status(500).send('BOT_TOKEN not set');
  }
  console.log('Webhook called', req.body);
  res.status(200).send('OK');

  try {
    const message = req.body.message;
    if (message && message.text === '/start') {
      const axios = require('axios');
      await axios.post(`https://tapi.bale.ai/bot${BOT_TOKEN}/sendMessage`, {
        chat_id: message.chat.id,
        text: 'سلام! ربات فعال است.'
      });
    }
  } catch (err) {
    console.error(err.message);
  }
};
