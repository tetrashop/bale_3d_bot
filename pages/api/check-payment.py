// pages/api/check-payment.js
import fs from 'fs';
import path from 'path';
import { paidTokens, pendingModels } from '../../lib/state';

// این تابع توسط Webhook بله صدا زده می‌شود
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { payload, status } = req.body;
  if (!payload || status !== 'PAID') return res.status(400).json({ error: 'Invalid payment status' });

  // استخراج token واقعی فایل از payload
  const token = payload.replace(/^PAY_/, '').split('_')[0];
  if (!token || !pendingModels.has(token)) {
    return res.status(404).json({ error: 'Model not found or expired' });
  }

  // ثبت پرداخت موفق برای این توکن
  paidTokens.set(token, Date.now()); // ثبت کاربر به عنوان پرداخت‌کننده

  try {
    const modelInfo = pendingModels.get(token);
    if (!modelInfo || !modelInfo.path) throw new Error('Model file missing');

    // [اختیاری] مسیر فایل OBJ‌هایی که پرداخت آن‌ها تأیید شده را در لاگ ذخیره کن
    const logPath = path.join(process.cwd(), 'public', 'paid_models.log');
    fs.appendFileSync(logPath, `${new Date().toISOString()} - ${token} - ${modelInfo.filename}\n`);
  } catch (err) {
    console.error('خطا در ذخیره لاگ پرداخت:', err);
  }

  return res.status(200).json({ success: true });
}
