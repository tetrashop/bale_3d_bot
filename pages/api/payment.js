// pages/api/payment.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { chatId, amount, description } = req.body;

  // اعتبارسنجی ورودی
  if (!chatId || typeof chatId !== 'string' || chatId.trim() === '') {
    return res.status(400).json({ error: 'chatId نامعتبر است' });
  }
  const numericAmount = Number(amount);
  if (isNaN(numericAmount) || numericAmount <= 0) {
    return res.status(400).json({ error: 'مبلغ باید یک عدد مثبت باشد' });
  }

  const BOT_TOKEN = process.env.BOT_TOKEN;
  const isProd = process.env.NODE_ENV === 'production';
  // توکن واقعی یا تست – هر دو از نوع WALLET-... هستند
  const providerToken = isProd ? process.env.PROVIDER_TOKEN_LIVE : process.env.PROVIDER_TOKEN_TEST;

  if (!BOT_TOKEN || !providerToken) {
    console.error('Missing BOT_TOKEN or PROVIDER_TOKEN');
    return res.status(500).json({ error: 'تنظیمات پرداخت کامل نیست' });
  }

  // ساخت فاکتور
  const invoicePayload = {
    chat_id: chatId,
    title: 'تبدیل تصویر به مدل سه‌بعدی',
    description: description || 'دریافت فایل OBJ پس از پرداخت',
    payload: `order_${chatId}_${Date.now()}`,
    provider_token: providerToken,
    currency: 'IRR',
    prices: JSON.stringify([{ label: 'یک بار تبدیل', amount: numericAmount * 10 }]), // ریال
    start_parameter: 'start_param'
  };

  try {
    const response = await fetch(`https://api.bale.ai/bot${BOT_TOKEN}/sendInvoice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(invoicePayload)
    });

    const data = await response.json();

    if (response.ok && data.ok) {
      return res.status(200).json({ ok: true, message: 'فاکتور ارسال شد' });
    } else {
      console.error('Invoice error:', data);
      return res.status(500).json({ error: 'خطا در ارسال فاکتور', details: data });
    }
  } catch (error) {
    console.error('Payment API error:', error);
    return res.status(500).json({ error: 'خطای داخلی سرور' });
  }
}
