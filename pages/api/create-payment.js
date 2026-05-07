export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { token } = req.body;
  if (!token) return res.status(400).json({ error: 'No token' });

  const txId = 'sim_' + Date.now() + '_' + Math.random().toString(36).substring(2);
  return res.status(200).json({ success: true, transactionId: txId, invoiceUrl: '#' });
}
