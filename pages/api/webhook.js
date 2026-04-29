// pages/api/webhook.js
import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFile, unlink } from 'fs/promises';
import fs from 'fs';
import path from 'path';
import os from 'os';

const execPromise = promisify(exec);

// توابع کمکی برای ارسال پیام و فایل به بله
async function sendMessage(chatId, text) {
  const botToken = process.env.BOT_TOKEN;
  if (!botToken) return;
  try {
    await fetch(`https://api.bale.ai/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text })
    });
  } catch (err) {
    console.error('sendMessage error:', err);
  }
}

async function sendDocument(chatId, filePath, caption = '') {
  const botToken = process.env.BOT_TOKEN;
  if (!botToken) return;
  try {
    const fileBuffer = await fs.promises.readFile(filePath);
    const formData = new FormData();
    formData.append('document', new Blob([fileBuffer]), path.basename(filePath));
    formData.append('chat_id', chatId);
    if (caption) formData.append('caption', caption);
    await fetch(`https://api.bale.ai/bot${botToken}/sendDocument`, {
      method: 'POST',
      body: formData
    });
  } catch (err) {
    console.error('sendDocument error:', err);
  }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const update = req.body;

    // ========== 1. مدیریت pre_checkout_query (تأیید پیش‌پرداخت) ==========
    if (update.pre_checkout_query) {
      const query = update.pre_checkout_query;
      const botToken = process.env.BOT_TOKEN;
      await fetch(`https://api.bale.ai/bot${botToken}/answerPreCheckoutQuery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pre_checkout_query_id: query.id,
          ok: true
        })
      });
      return res.status(200).json({ ok: true });
    }

    // ========== 2. مدیریت پرداخت موفق ==========
    if (update.message && update.message.successful_payment) {
      const chatId = update.message.chat.id;
      const payment = update.message.successful_payment;
      const transactionId = payment.provider_payment_charge_id;
      console.log(`✅ پرداخت موفق برای کاربر ${chatId} - تراکنش: ${transactionId}`);

      const modelPath = path.join(process.cwd(), 'public/models/3d_object.obj');
      if (fs.existsSync(modelPath)) {
        await sendDocument(chatId, modelPath, '✅ مدل سه‌بعدی شما – با تشکر از پرداخت');
      } else {
        await sendMessage(chatId, '❌ مدل ساخته نشده است. لطفاً دوباره تلاش کنید.');
      }
      return res.status(200).json({ ok: true });
    }

    // ========== 3. مدیریت پیام‌های معمولی (عکس، متن) ==========
    const message = update.message;
    if (!message) {
      return res.status(200).json({ ok: true, message: 'No message' });
    }

    // اگر متن ساده بود (مثلاً /start)
    if (message.text) {
      const text = message.text.trim();
      if (text === '/start') {
        await sendMessage(message.chat.id, 'سلام! لطفاً یک تصویر از مگس ارسال کنید تا مدل سه‌بعدی ساخته شود.');
      }
      return res.status(200).json({ ok: true });
    }

    // اگر عکس داشت
    if (message.photo) {
      const chatId = message.chat.id;
      const fileId = message.photo[message.photo.length - 1].file_id;
      const botToken = process.env.BOT_TOKEN;

      // 1. دریافت اطلاعات فایل
      const fileInfoRes = await fetch(`https://api.bale.ai/bot${botToken}/getFile?file_id=${fileId}`);
      const fileInfo = await fileInfoRes.json();
      if (!fileInfo.ok) throw new Error('Failed to get file info');

      const fileUrl = `https://api.bale.ai/file/bot${botToken}/${fileInfo.result.file_path}`;
      const imageRes = await fetch(fileUrl);
      const imageBuffer = Buffer.from(await imageRes.arrayBuffer());

      // 2. ذخیره موقت
      const tempImagePath = path.join(os.tmpdir(), `${chatId}_${Date.now()}.jpg`);
      await writeFile(tempImagePath, imageBuffer);

      // 3. مسیر خروجی OBJ
      const outputObjPath = path.join('/tmp', `model_${chatId}_${Date.now()}.obj`);
      const pythonScript = path.join(process.cwd(), 'engine_3d.py');
      const command = `python3 "${pythonScript}" "${tempImagePath}" "${outputObjPath}"`;

      console.log('Executing Python script:', command);
      const { stdout, stderr } = await execPromise(command, { timeout: 60000 });
      if (stderr) console.error('Python stderr:', stderr);
      console.log('Python stdout:', stdout);

      // 4. ارسال فایل OBJ به کاربر
      if (fs.existsSync(outputObjPath)) {
        await sendDocument(chatId, outputObjPath, '✅ مدل سه‌بعدی شما آماده است');
      } else {
        await sendMessage(chatId, '❌ خطا در ساخت مدل. لطفاً دوباره تلاش کنید.');
      }

      // 5. پاکسازی فایل‌های موقت
      await unlink(tempImagePath).catch(() => {});
      await unlink(outputObjPath).catch(() => {});

      return res.status(200).json({ ok: true });
    }

    // در غیر این صورت
    return res.status(200).json({ ok: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return res.status(500).json({ error: error.message });
  }
}
