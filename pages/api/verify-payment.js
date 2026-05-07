// pages/api/verify-payment.js
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { transactionId } = req.body;
  const processorUrl = process.env.PROCESSOR_API_URL;

  if (!processorUrl) {
    // شبیه‌سازی موفقیت
    return res.status(200).json({ success: true });
  }

  try {
    const response = await fetch(`${processorUrl}/check-payment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transaction_id: transactionId }),
    });
    const data = await response.json();
    if (response.ok && data.paid) {
      return res.status(200).json({ success: true });
    } else {
      return res.status(400).json({ error: 'Payment not completed' });
    }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Verification failed' });
  }
}
