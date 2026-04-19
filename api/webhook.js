const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// پاسخ برای روت /
app.get('/', (req, res) => {
  res.send('Server is running!');
});

// پاسخ برای وب‌هوک بله
app.post('/api/webhook', (req, res) => {
  const body = req.body;
  console.log('Received webhook:', body);

  if (!body) return res.status(400).send('No body');

  return res.status(200).json({
    method: "sendMessage",
    chat_id: body.chat?.id || 0,
    text: "سلام! پیام شما دریافت شد."
  });
});

module.exports = app;
