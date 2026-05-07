// pages/api/payment.js
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { amount, currency, walletId } = req.body;
  const processorUrl = process.env.PROCESSOR_API_URL;
  const botToken = process.env.BOT_TOKEN;
  const providerToken = process.env.PROVIDER_TOKEN_LIVE || process.env.PROVIDER_TOKEN_TEST;

  if (!processorUrl) {
    // شبیه‌سازی موفقیت در صورت نبود API واقعی (برای تست سریع)
    console.warn('PROCESSOR_API_URL not set, simulating success');
    return res.status(200).json({ success: true, transactionId: 'sim_' + Date.now() });
  }

  try {
    const response = await fetch(`${processorUrl}/create-invoice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount,
        currency,
        wallet_id: walletId,
        bot_token: botToken,
        provider_token: providerToken,
      }),
    });
    const data = await response.json();
    if (response.ok && data.success) {
      return res.status(200).json({ success: true, invoiceUrl: data.invoice_url, transactionId: data.id });
    } else {
      return res.status(400).json({ error: data.error || 'Payment creation failed' });
    }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Payment processor error' });
  }
}
