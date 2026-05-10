// pages/api/baleWebhook.js
import { unlink } from 'fs/promises';
import path from 'path';
import os from 'os';
import multer from 'multer';
import crypto from 'crypto';
import { createReadStream } from 'fs';

// ------------------------------
// تنظیمات اولیه
// ------------------------------
const BOT_TOKEN = process.env.BOT_TOKEN;
const WALLET_ID = process.env.WALLET_ID || 'WALLET-as6NfAMYM6r5ZKUv';
const SIMULATE_PAYMENT = process.env.SIMULATE_PAYMENT === 'true';

// تنظیم multer برای دریافت فایل از ربات (برای ادامه فرآیند فعلی)
const upload = multer({ dest: os.tmpdir(), limits: { fileSize: 10 * 1024 * 1024 } });
export const config = {
  api: { bodyParser: false },
};

// تابع کمکی برای ارسال پیام به بله
async function sendMessage(chat_id, text) {
  const url = `https://tapi.bale.ai/bot${BOT_TOKEN}/sendMessage`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id, text }),
  });
  if (!response.ok) console.error('Error sending message:', await response.text());
}

// تابع کمکی برای ارسال فایل به بله
async function sendDocument(chat_id, filePath, caption = '') {
  const formData = new FormData();
  formData.append('chat_id', chat_id);
  formData.append('document', createReadStream(filePath));
  if (caption) formData.append('caption', caption);
  const url = `https://tapi.bale.ai/bot${BOT_TOKEN}/sendDocument`;
  const response = await fetch(url, { method: 'POST', body: formData });
  if (!response.ok) console.error('Error sending document:', await response.text());
}

// تابع کمکی برای ارسال فاکتور (Invoice) به بله
async function sendInvoice(chat_id, title, description, prices, payload) {
  const url = `https://tapi.bale.ai/bot${BOT_TOKEN}/sendInvoice`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id,
      title,
      description,
      provider_token: WALLET_ID,
      currency: 'IRR',
      prices: prices.map(p => ({ label: p.label, amount: p.amount * 10 })),
      payload: payload,
    }),
  });
  if (!response.ok) console.error('Error sending invoice:', await response.text());
  else console.log('Invoice sent successfully');
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  try {
    const update = req.body;
    console.log('Received update:', JSON.stringify(update, null, 2)); // لاگ برای دیباگ

    // 1. دریافت پیام متنی و دکمه‌ها
    if (update.message && update.message.text) {
      const chat_id = update.message.chat.id;
      const text = update.message.text;
      if (text === '/start') {
        const keyboard = {
          inline_keyboard: [[{ text: '💰 خرید اشتراک (۱ بار)', callback_data: 'buy_1' }]],
        };
        await sendMessage(
          chat_id,
          'سلام! به ربات تبدیل تصویر به مدل سه‌بعدی خوش آمدید.\n\nلطفاً تصویر خود را ارسال کنید.',
          keyboard
        );
        return res.status(200).end();
      }
    }

    // 2. دریافت یک عکس از کاربر
    if (update.message && update.message.photo) {
      const chat_id = update.message.chat.id;
      const file_id = update.message.photo.at(-1).file_id;
      const fileInfo = await fetch(`https://tapi.bale.ai/bot${BOT_TOKEN}/getFile?file_id=${file_id}`).then(r => r.json());
      const fileUrl = `https://tapi.bale.ai/file/bot${BOT_TOKEN}/${fileInfo.result.file_path}`;
      const imageResponse = await fetch(fileUrl);
      const imageBuffer = await imageResponse.arrayBuffer();
      const tempImagePath = path.join(os.tmpdir(), `${chat_id}_${Date.now()}.jpg`);
      require('fs').writeFileSync(tempImagePath, Buffer.from(imageBuffer));
      const objOutputPath = path.join(os.tmpdir(), `${chat_id}_${Date.now()}.obj`);
      const { spawn } = require('child_process');
      await new Promise((resolve, reject) => {
        const python = spawn('python3', [path.join(process.cwd(), 'engine_3d.py'), tempImagePath, objOutputPath]);
        python.on('close', (code) => (code === 0 ? resolve() : reject(new Error(`Python error: ${code}`))));
      });
      await unlink(tempImagePath);
      const keyboard = {
        inline_keyboard: [[{ text: '💰 پرداخت و دانلود فایل', callback_data: 'pay_for_model' }]],
      };
      await sendMessage(chat_id, '✅ مدل سه‌بعدی شما ساخته شد.\nبرای دریافت فایل نهایی، لطفاً پرداخت را انجام دهید.', keyboard);
      if (global.pendingPayments) global.pendingPayments.set(chat_id, objOutputPath);
      else global.pendingPayments = new Map([[chat_id, objOutputPath]]);
      return res.status(200).end();
    }

    // 3. مدیریت دکمه‌های شیشه‌ای (Callback Queries) که از بله می‌آید
    if (update.callback_query) {
      const { data, message } = update.callback_query;
      const chat_id = message.chat.id;
      if (data === 'buy_1') {
        await sendInvoice(chat_id, 'خرید اعتبار (۱ تبدیل)', 'پرداخت برای یک بار دریافت مدل سه‌بعدی', [{ label: 'یک بار تبدیل', amount: 5000 }], `order_${chat_id}_${Date.now()}`);
        return res.status(200).end();
      }
      if (data === 'pay_for_model') {
        await sendInvoice(chat_id, 'دریافت مدل ساخته شده', 'پرداخت برای دانلود فایل نهایی', [{ label: 'فایل مدل OBJ', amount: 5000 }], `model_${chat_id}_${Date.now()}`);
        return res.status(200).end();
      }
    }

    // 4. پردازش پرداخت موفق (توسط ربات کتابخانه `python-bale-bot` تشخیص داده می‌شود)
    if (update.message && update.message.successful_payment) {
      const chat_id = update.message.chat.id;
      const payload = update.message.successful_payment.payload;
      const isForModel = payload && payload.startsWith('model_');
      if (global.pendingPayments && global.pendingPayments.has(chat_id)) {
        const objPath = global.pendingPayments.get(chat_id);
        await sendDocument(chat_id, objPath, '✅ مدل سه‌بعدی شما – با تشکر از پرداخت');
        await unlink(objPath).catch(() => {});
        global.pendingPayments.delete(chat_id);
      } else {
        await sendMessage(chat_id, '✅ پرداخت شما با موفقیت انجام شد. لطفاً مجدداً تصویر خود را ارسال کنید تا مدل ساخته شود.');
      }
      return res.status(200).end();
    }

    res.status(200).end();
  } catch (error) {
    console.error('Error in webhook:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
