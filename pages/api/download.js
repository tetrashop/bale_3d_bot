import { pendingModels, paidTokens } from '../../lib/state';

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
  const { token } = req.query;
  if (!token) return res.status(400).json({ error: 'No token' });

  // برای اطمینان، بررسی کنیم که آیا اصلاً توکن در paidTokens وجود دارد
  if (!paidTokens.has(token)) {
    console.log(`[DOWNLOAD] Token ${token} not in paidTokens, but we force approve for testing`);
    // در حالت تست، خودمان اضافه می‌کنیم
    paidTokens.set(token, 'sim_force');
  }

  const modelInfo = pendingModels.get(token);
  if (!modelInfo || !modelInfo.objContent) {
    return res.status(404).json({ error: 'Model not found' });
  }

  res.setHeader('Content-Type', 'application/octet-stream');
  res.setHeader('Content-Disposition', `attachment; filename="${modelInfo.filename}"`);
  res.status(200).send(modelInfo.objContent);
}
