import fs from 'fs';
import path from 'path';

// این یک نمونه ساده است – توصیه می‌شود توکن را در دیتابیس ذخیره کنید
export default async function handler(req, res) {
  const { token } = req.query;
  if (!token) return res.status(400).send('توکن نامعتبر');

  // در عمل باید اعتبار توکن را بررسی کنید (مثلاً از دیتابیس)
  // برای نمونه، یک فایل موقت OBJ را که قبلاً در سرویس پایتون ساخته شده است،
  // باید از طریق یک API دیگر از سرویس پایتون دریافت کنید یا قبلاً ذخیره کرده باشید.
  // اینجا فرض می‌کنیم مدل در public/models/3d_object.obj موجود است.
  const filePath = path.join(process.cwd(), 'public/models/3d_object.obj');
  if (fs.existsSync(filePath)) {
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', 'attachment; filename=3d_object.obj');
    fs.createReadStream(filePath).pipe(res);
  } else {
    res.status(404).send('فایل یافت نشد');
  }
}
