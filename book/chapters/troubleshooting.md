# رفع مشکلات رایج

در هنگام اجرای پروژه ممکن است به مشکلات زیر برخورد کنید:

## خطای دسترسی (EACCES)

- پیام خطا: `EACCES: permission denied`  
- راه حل: دسترسی ترموکس به حافظه را فعال کنید:  
  ```bash
  termux-setup-storage
  chmod -R u+rw ~/bale_3d_bot

سپس ترموکس را ببندید و دوباره باز کنید.
خطای پورت اشغال شده
اگر پورت 3000 در حال استفاده باشد، Next.js به پورت‌های بعدی مثل 3001 می‌رود. کافی‌ست با پورت جدید به آدرس بروید.
خطای Watchpack و عدم بازخوانی خودکار (hot-reload)
سیستم فایل اندروید ممکن است به خوبی قابلیت دنبال کردن تغییرات را نداشته باشد.
در فایل next.config.js مقادیر polling را اضافه کنید:
module.exports = {
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      };
    }
    return config;
  },
};

