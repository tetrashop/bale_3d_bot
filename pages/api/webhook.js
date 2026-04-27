// pages/api/webhook.js
import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFile, unlink } from 'fs/promises';
import path from 'path';
import os from 'os';

const execPromise = promisify(exec);

export default async function handler(req, res) {
  // فقط درخواست‌های POST را قبول کن
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const update = req.body;

    // بررسی وجود پیام و عکس
    const message = update.message;
    if (!message || !message.photo) {
      return res.status(200).json({ ok: true, message: 'No photo' });
    }

    const chatId = message.chat.id;
    const fileId = message.photo[message.photo.length - 1].file_id;

    // 1. دریافت اطلاعات فایل از بله
    const BOT_TOKEN = process.env.BOT_TOKEN;
    if (!BOT_TOKEN) {
      throw new Error('BOT_TOKEN not set');
    }

    const fileInfoRes = await fetch(`https://api.bale.ai/bot${BOT_TOKEN}/getFile?file_id=${fileId}`);
    const fileInfo = await fileInfoRes.json();

    if (!fileInfo.ok) {
      throw new Error('Failed to get file info');
    }

    const fileUrl = `https://api.bale.ai/file/bot${BOT_TOKEN}/${fileInfo.result.file_path}`;
    const imageRes = await fetch(fileUrl);
    const imageBuffer = Buffer.from(await imageRes.arrayBuffer());

    // 2. ذخیره موقت عکس
    const tempImagePath = path.join(os.tmpdir(), `${chatId}_${Date.now()}.jpg`);
    await writeFile(tempImagePath, imageBuffer);

    // 3. مسیر خروجی مدل OBJ (در /tmp برای Vercel)
    const outputObjPath = path.join('/tmp', `model_${chatId}_${Date.now()}.obj`);

    // 4. اجرای اسکریپت پایتون
    const pythonScript = path.join(process.cwd(), 'engine_3d.py');
    const command = `python3 "${pythonScript}" "${tempImagePath}" "${outputObjPath}"`;

    console.log('Executing Python script:', command);
    const { stdout, stderr } = await execPromise(command, { timeout: 60000 });

    if (stderr) {
      console.error('Python stderr:', stderr);
    }
    console.log('Python stdout:', stdout);

    // 5. ارسال فایل OBJ به کاربر
    const fs = require('fs');
    if (fs.existsSync(outputObjPath)) {
      const fileBuffer = await fs.promises.readFile(outputObjPath);
      const formData = new FormData();
      formData.append('document', new Blob([fileBuffer]), 'model.obj');
      formData.append('chat_id', chatId);
      formData.append('caption', '✅ مدل سه‌بعدی شما آماده است');

      await fetch(`https://api.bale.ai/bot${BOT_TOKEN}/sendDocument`, {
        method: 'POST',
        body: formData,
      });
    } else {
      throw new Error('Output OBJ file not created');
    }

    // 6. پاکسازی فایل‌های موقت
    await unlink(tempImagePath).catch(() => {});
    await unlink(outputObjPath).catch(() => {});

    return res.status(200).json({ ok: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return res.status(500).json({ error: error.message });
  }
}
