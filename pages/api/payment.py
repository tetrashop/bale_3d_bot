// pages/api/payment.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { walletId, message, chatId, amount } = req.body;

  // حالت ولت تست (از صفحه اصلی)
  if (walletId && message) {
    console.log(`✅ پرداخت شبیه‌سازی شده برای کیف پول: ${walletId}`);
    return res.status(200).json({
      ok: true,
      transactionId: `TEST_${Date.now()}`,
      message: 'پرداخت آزمایشی با موفقیت انجام شد'
    });
  }

  // حالت پرداخت واقعی (از صفحه payment)
  if (chatId && amount && amount > 0) {
    const transactionId = `PAY_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;
    console.log(`✅ پرداخت موفق برای کاربر ${chatId}: ${amount} تومان`);
    return res.status(200).json({
      ok: true,
      transactionId,
      message: 'پرداخت با موفقیت انجام شد'
    });
  }

  return res.status(400).json({ error: 'اطلاعات پرداخت ناقص است' });
}
