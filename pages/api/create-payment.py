// pages/api/create-payment.js
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { token } = req.body;
  if (!token) return res.status(400).json({ error: 'شناسه پرداخت نامعتبر است' });

  const BOT_TOKEN = process.env.BOT_TOKEN;
  const WALLET_ID = process.env.WALLET_ID;
  const PRICE_IRR = parseInt(process.env.PRICE_IRR || '50000', 10); // مبلغ به ریال
  const PAYLOAD = `PAY_${token}_${Date.now()}`;

  if (!BOT_TOKEN || !WALLET_ID) {
    console.error("❌ BOT_TOKEN یا WALLET_ID تنظیم نشده است.");
    return res.status(500).json({ error: 'تنظیمات سرور ناقص است' });
  }

  // آماده‌سازی داده‌ها برای ارسال به API ربات بله
  const invoiceData = {
    chat_id: req.body.user_chat_id, // شناسه چت کاربر در پیام‌رسان بله
    title: "مدل سه‌بعدی سفارشی",
    description: "پرداخت برای دریافت فایل سه‌بعدی OBJ",
    provider_token: WALLET_ID,
    payload: PAYLOAD,
    prices: [{ label: "مدل OBJ", amount: PRICE_IRR }],
    start_parameter: "convert_3d",
    currency: "IRR"
  };

  try {
    // ارسال درخواست ساخت و ارسال فاکتور به API رسمی بله
    const apiResponse = await fetch(`https://tapi.bale.ai/bot${BOT_TOKEN}/sendInvoice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(invoiceData)
    });

    const responseData = await apiResponse.json();

    if (responseData.ok) {
      return res.status(200).json({
        success: true,
        transactionId: PAYLOAD,
        paymentRequestSent: true
      });
    } else {
      console.error('خطا در ارسال فاکتور:', responseData);
      return res.status(500).json({ error: 'خطا در ایجاد درخواست پرداخت' });
    }
  } catch (err) {
    console.error('خطا در ارتباط با سرور بله:', err);
    return res.status(500).json({ error: 'خطا در ارتباط با درگاه پرداخت' });
  }
}
