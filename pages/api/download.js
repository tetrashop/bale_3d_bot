import { pendingModels, paidTokens } from '../../lib/state';
export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
  const { token } = req.query;
  if (!token) return res.status(400).json({ error: 'No token' });
  if (!paidTokens.has(token)) {
    return res.status(402).json({ error: 'Payment required' });
  }
  const model = pendingModels.get(token);
  if (!model || !model.objContent) {
    return res.status(404).json({ error: 'Model not found' });
  }
  res.setHeader('Content-Type', 'application/octet-stream');
  res.setHeader('Content-Disposition', `attachment; filename="${model.filename}"`);
  res.status(200).send(model.objContent);
}
