// pages/api/baleWebhook.js

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { body } = req;
    // فرض می‌کنیم پیام در body.message.text هست
    const userMessage = body.message?.text || '';

    // منطق ساده پاسخ دادن
    const replyText = `پیام شما دریافت شد: ${userMessage}`;

    // ساختار پاسخ به بله (مثال برای پیام متنی)
    const responsePayload = {
      status: 0,
      body: {
        messages: [
          {
            type: 'text',
            text: replyText
          }
        ]
      }
    };

    res.status(200).json(responsePayload);
  } catch (error) {
    console.error('Error in baleWebhook:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
