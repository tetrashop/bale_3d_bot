export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { token, quality, chatId } = req.body;
  if (!token || !chatId) return res.status(400).json({ error: 'Missing chatId or token' });

  const BOT_TOKEN = process.env.BOT_TOKEN;
  const WALLET_ID = process.env.WALLET_ID;
  if (!BOT_TOKEN || !WALLET_ID) return res.status(500).json({ error: 'Payment config missing' });

  const prices = { normal: 500000, high: 15000000, pro: 3000000 };
  const amount = prices[quality] || 500000;
  const payload = `PAY_${token}_${Date.now()}`;

  try {
    const response = await fetch(`https://tapi.bale.ai/bot${BOT_TOKEN}/sendInvoice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        title: `مدل سه‌بعدی (${quality})`,
        description: "فایل OBJ نقش برجسته",
        provider_token: WALLET_ID,
        payload: payload,
        prices: [{ label: "مدل OBJ", amount }],
        start_parameter: "convert_3d",
        currency: "IRR"
      })
    });
    const data = await response.json();
    if (data.ok) {
      return res.status(200).json({ success: true, transactionId: payload });
    } else {
      console.error('Invoice error:', data);
      return res.status(500).json({ error: 'خطا در ایجاد فاکتور' });
    }
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'خطا در ارتباط با درگاه' });
  }
}
