export const maxDuration = 60; // افزایش زمان اجرا به 60 ثانیه
import { IncomingForm } from 'formidable';
import fs from 'fs';
import path from 'path';
export const config = { api: { bodyParser: false } };

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const form = new IncomingForm();
  form.parse(req, async (err, fields, files) => {
    if (err) return res.status(400).json({ error: err.message });

    // پیام بله به صورت JSON در fields.message است (اگر از وب‌هوک استاندارد استفاده کنید)
    // در اینجا یک نمونه ساده فرض می‌کنیم که فایل تصویر در files عکس است.
    const file = files.photo?.[0] || files.document?.[0];
    if (!file) {
      return res.status(200).json({ ok: true });
    }

    const chatId = fields.chat_id?.[0];
    if (!chatId) return res.status(200).json({ ok: true });

    // ارسال تصویر به سرویس پردازش پایتون
    const formData = new FormData();
    formData.append('image', fs.createReadStream(file.filepath), file.originalFilename);

    const processorUrl = process.env.PROCESSOR_API_URL;
    if (!processorUrl) return res.status(500).json({ error: 'Processor API missing' });

    try {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error('Processing failed');

      const blob = await response.arrayBuffer();
      // ذخیره موقت فایل OBJ برای ارسال به کاربر
      const tempObjPath = path.join('/tmp', `${chatId}_model.obj`);
      fs.writeFileSync(tempObjPath, Buffer.from(blob));

      // ارسال فایل به کاربر در بله (با استفاده از توکن ربات)
      const botToken = process.env.BOT_TOKEN;
      if (botToken) {
        const sendDoc = await fetch(`https://api.bale.ai/bot${botToken}/sendDocument`, {
          method: 'POST',
          body: new FormData().append('document', fs.createReadStream(tempObjPath), 'model.obj'),
        });
        console.log(await sendDoc.text());
      }
      // پاکسازی فایل موقت
      fs.unlinkSync(tempObjPath);
    } catch (error) {
      console.error(error);
    }

    res.status(200).json({ ok: true });
  });
}
