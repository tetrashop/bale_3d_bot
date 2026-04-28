export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { walletId, message } = req.body;
  if (walletId && message) {
    console.log(`✅ پرداخت شبیه‌سازی شده برای ${walletId}`);
    return res.status(200).json({ ok: true, transactionId: `test_${Date.now()}` });
  }
  return res.status(400).json({ error: 'Invalid payment data' });
}
