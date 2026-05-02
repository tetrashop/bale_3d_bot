export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const walletId = process.env.WALLET_ID || 'WALLET-as6NfAMYM6r5ZKUv';
  const amount = 5000;
  const callbackUrl = `${process.env.NEXTAUTH_URL || 'https://your-domain.vercel.app'}/api/verifyPayment`;

  try {
    const response = await fetch('https://api.bale.ai/v1/payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        walletId,
        amount,
        callbackUrl,
        description: 'خرید مدل سه‌بعدی',
      }),
    });
    const data = await response.json();
    if (data.paymentUrl) {
      res.status(200).json({ paymentUrl: data.paymentUrl });
    } else {
      res.status(500).json({ error: 'پرداخت ناموفق' });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
