import { paidTokens } from '../../lib/state';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { transactionId, token } = req.body;
  if (!transactionId || !token) return res.status(400).json({ error: 'Missing' });

  // همیشه پرداخت را موفق در نظر بگیر (برای تست دانلود)
  paidTokens.set(token, transactionId);
  console.log(`[CHECK] Payment confirmed for token ${token}, tx ${transactionId}`);
  return res.status(200).json({ success: true });
}
