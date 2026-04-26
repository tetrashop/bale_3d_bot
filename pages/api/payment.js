// pages/api/payment.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { chatId, amount, walletId, message } = req.body;

  // حالت اول: درخواست از دکمه ولت تست (ارسال walletId و message)
  if (walletId && message) {
    console.log(`✅ Simulated payment for wallet: ${walletId}`);
    return res.status(200).json({
      ok: true,
      transactionId: `TEST_${Date.now()}`,
      message: 'پرداخت آزمایشی با موفقیت انجام شد'
    });
  }

  // حالت دوم: درخواست از صفحه پرداخت واقعی (ارسال chatId و amount)
  if (chatId && typeof amount === 'number' && amount > 0) {
    const transactionId = `PAY_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
    console.log(`✅ Payment: ${chatId} - ${amount} تومان`);
    return res.status(200).json({ ok: true, transactionId });
  }

  // در غیر این صورت خطا بده
  return res.status(400).json({ error: 'Invalid request: missing chatId+amount or walletId+message' });
}
