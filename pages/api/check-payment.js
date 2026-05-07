import { paidTokens, pendingModels } from '../../lib/state';
import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { payload, status } = req.body;
  if (status !== 'PAID') return res.status(200).json({ ok: true });

  const token = payload.replace(/^PAY_/, '').split('_')[0];
  if (!token || !pendingModels.has(token)) {
    return res.status(404).json({ error: 'Invalid token' });
  }
  paidTokens.set(token, Date.now());
  const logPath = path.join(process.cwd(), 'public', 'paid.log');
  fs.appendFileSync(logPath, `${new Date().toISOString()} - ${token}\n`);
  return res.status(200).json({ success: true });
}
