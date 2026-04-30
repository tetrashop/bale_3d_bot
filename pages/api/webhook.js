import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFile, unlink } from 'fs/promises';
import fs from 'fs';
import path from 'path';
import os from 'os';

const execPromise = promisify(exec);

async function sendMessage(chatId, text, replyMarkup = null) {
  const botToken = process.env.BOT_TOKEN;
  if (!botToken) return;
  const body = { chat_id: chatId, text };
  if (replyMarkup) body.reply_markup = JSON.stringify(replyMarkup);
  try {
    await fetch(`https://api.bale.ai/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
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

    // مدیریت pre_checkout_query (تأیید پیش‌پرداخت)
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

    // مدیریت پرداخت موفق
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

    const message = update.message;
    if (!message) {
      return res.status(200).json({ ok: true, message: 'No message' });
    }

    // ========== مدیریت پیام‌های متنی (دستور /start) ==========
    if (message.text) {
      const text = message.text.trim();
      const chatId = message.chat.id;

      if (text === '/start') {
        const keyboard = {
          inline_keyboard: [[{
            text: "✨ ساخت مدل سه‌بعدی",
            web_app: { url: `https://bale-3d-bot.vercel.app/?chatId=${chatId}` }
          }]]
        };
        await sendMessage(chatId, "به ربات تبدیل 2D به 3D خوش آمدید. برای شروع، روی دکمه زیر کلیک کنید:", keyboard);
        return res.status(200).json({ ok: true });
      }
    }

    // ========== مدیریت پیام‌های حاوی عکس ==========
    if (!message.photo) {
      return res.status(200).json({ ok: true, message: 'No photo' });
    }

    const chatId = message.chat.id;
    const fileId = message.photo[message.photo.length - 1].file_id;
    const botToken = process.env.BOT_TOKEN;

    // دریافت فایل از بله
    const fileInfoRes = await fetch(`https://api.bale.ai/bot${botToken}/getFile?file_id=${fileId}`);
    const fileInfo = await fileInfoRes.json();
    if (!fileInfo.ok) throw new Error('Failed to get file info');

    const fileUrl = `https://api.bale.ai/file/bot${botToken}/${fileInfo.result.file_path}`;
    const imageRes = await fetch(fileUrl);
    const imageBuffer = Buffer.from(await imageRes.arrayBuffer());

    // ذخیره موقت
    const tempImagePath = path.join(os.tmpdir(), `${chatId}_${Date.now()}.jpg`);
    await writeFile(tempImagePath, imageBuffer);

    // مسیر خروجی OBJ
    const outputObjPath = path.join('/tmp', `model_${chatId}_${Date.now()}.obj`);
    const pythonScript = path.join(process.cwd(), 'engine_3d.py');
    const command = `python3 "${pythonScript}" "${tempImagePath}" "${outputObjPath}"`;

    console.log('Executing Python script:', command);
    const { stdout, stderr } = await execPromise(command, { timeout: 60000 });
    if (stderr) console.error('Python stderr:', stderr);
    console.log('Python stdout:', stdout);

    // ارسال مدل به کاربر
    if (fs.existsSync(outputObjPath)) {
      await sendDocument(chatId, outputObjPath, '✅ مدل سه‌بعدی شما آماده است');
    } else {
      await sendMessage(chatId, '❌ خطا در ساخت مدل. لطفاً دوباره تلاش کنید.');
    }

    // پاکسازی فایل‌های موقت
    await unlink(tempImagePath).catch(() => {});
    await unlink(outputObjPath).catch(() => {});

    return res.status(200).json({ ok: true });
  } catch (error) {
    console.error('Webhook error:', error);
    return res.status(500).json({ error: error.message });
  }
}
