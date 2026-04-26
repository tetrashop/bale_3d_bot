import fetch from 'node-fetch';

const BALE_BOT_TOKEN = process.env.BALE_BOT_TOKEN;

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method Not Allowed" });
  }

  const { walletId, message } = req.body;
  if (!walletId || !message) {
    return res.status(400). json({ error: "Missing walletId or message" });
  }

  // ✅ اصلاح آدرس API
  const API_URL = `https://api.bale.ai/v1/bot-message-send`;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${BALE_BOT_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ to: walletId, type: "Text", text: message }),
    });

    if (!response.ok) {
      const errTxt = await response.text();
      return res.status(500).json({ error: `Send message failed: ${errTxt}` });
    }

    const data = await response.json();
    res.status(200).json(data);
  } catch (err) {
    console.error("Payment API error:", err);
    res.status(500).json({ error: err.message });
  }
}
