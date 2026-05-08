import fs from 'fs';
import path from 'path';

// یک Map ساده برای توکن‌های معتبر (در حافظه)
const validTokens = new Map();

// این تابع باید در verifyPayment اجرا شود (برای سادگی، فعلاً هر توکنی قبول می‌شود)
export default function handler(req, res) {
  const { token } = req.query;
  if (!token) return res.status(400).send('توکن نامعتبر');

  // در عمل باید اعتبار token را بررسی کنی (مثلاً از دیتابیس)
  // برای نمونه هر توکنی قبول می‌کنیم:
  const filePath = path.join(process.cwd(), 'public/models/3d_object.obj');
  if (fs.existsSync(filePath)) {
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', 'attachment; filename=3d_object.obj');
    fs.createReadStream(filePath).pipe(res);
  } else {
    res.status(404).send('فایل یافت نشد');
  }
}
