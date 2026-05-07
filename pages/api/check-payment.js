import { paidTokens } from '../../lib/state';
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { transactionId, token } = req.body;
  if (!transactionId || !token) return res.status(400).json({ error: 'Missing' });
  paidTokens.set(token, transactionId);
  return res.status(200).json({ success: true });
}
