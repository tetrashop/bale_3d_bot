const axios = require('axios');

// دریافت توکن از متغیر محیطی در Vercel
const BOT_TOKEN = process.env.BOT_TOKEN;
if (!BOT_TOKEN) {
  console.error("FATAL: BOT_TOKEN environment variable is not set.");
}

const BALE_API_URL = `https://tapi.bale.ai/bot${BOT_TOKEN}`;

// تابع کمکی برای ارسال درخواست به API Bale
async function callBaleApi(method, params) {
  try {
    const response = await axios.post(`${BALE_API_URL}/${method}`, params);
    return response.data;
  } catch (error) {
    console.error(`Error calling Bale API method ${method}:`, error.response?.data || error.message);
    return null;
  }
}

// تابع اصلی وب‌هوک که Vercel آن را فراخوانی می‌کند
module.exports = async (req, res) => {
  // فقط درخواست‌های POST را پردازش کن
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const update = req.body;
  console.log("Received update:", JSON.stringify(update));

  // پاسخ سریع به Bale برای تایید دریافت (با کد 200)
  res.status(200).send('OK');

  // پردازش آپدیت در پس‌زمینه بعد از ارسال پاسخ
  try {
    // بررسی وجود پیام
    if (!update.message) {
      console.log("No message in update.");
      return;
    }

    const message = update.message;
    const chatId = message.chat.id;

    // مدیریت دستور /start
    if (message.text === '/start') {
      await callBaleApi('sendMessage', {
        chat_id: chatId,
        text: "سلام! من ربات تبدیل 2D به 3D هستم. یک عکس برای من بفرستید."
      });
      return;
    }

    // مدیریت عکس دریافتی
    if (message.photo) {
      // بزرگترین سایز عکس را انتخاب کن
      const photo = message.photo[message.photo.length - 1];
      const fileId = photo.file_id;

      // دریافت مسیر فایل برای دانلود
      const fileInfo = await callBaleApi('getFile', { file_id: fileId });
      if (!fileInfo || !fileInfo.result || !fileInfo.result.file_path) {
        await callBaleApi('sendMessage', {
          chat_id: chatId,
          text: "خطایی در دریافت فایل رخ داد. لطفا دوباره تلاش کنید."
        });
        return;
      }

      // ساخت آدرس دانلود فایل
      const fileUrl = `https://tapi.bale.ai/file/bot${BOT_TOKEN}/${fileInfo.result.file_path}`;
      
      // در اینجا باید عملیات تبدیل 2D به 3D انجام شود.
      // فعلاً یک پیام آزمایشی ارسال می‌کنیم.
      await callBaleApi('sendMessage', {
        chat_id: chatId,
        text: `عکس شما با موفقیت دریافت شد. (file_id: ${fileId})\nلطفاً صبر کنید... در حال پردازش 2D به 3D.`
      });

      // TODO: دانلود فایل از fileUrl، پردازش و ارسال نتیجه به عنوان سند یا عکس
      
    } else {
      // پیام‌های دیگر
      await callBaleApi('sendMessage', {
        chat_id: chatId,
        text: "لطفا یک عکس برای من بفرستید یا از دستور /start استفاده کنید."
      });
    }
  } catch (error) {
    console.error("Error processing update in background:", error);
  }
};
