# تبدیل تصاویر دو بعدی به مدل‌های سه‌بعدی

## مستند کامل پروژه – نسخه نهایی (Relief Sculpture + شبیه‌سازی پرداخت)

**نویسنده:** رامین اجلال  
**آخرین بروزرسانی:** اردیبهشت ۱۴۰۴  
**مخزن:** [github.com/tetrashop/bale_3d_bot](https://github.com/tetrashop/bale_3d_bot)

---

## 🧠 معماری نهایی

| لایه | فناوری | وظیفه |
|------|--------|--------|
| Frontend | Next.js + React | آپلود تصویر، نمایش پیش‌نمایش Three.js، فرم پرداخت |
| Backend API | Next.js API Routes | دریافت تصویر، فراخوانی موتور پایتون، مدیریت توکن‌ها |
| موتور تبدیل | Python + `engine_3d.py` | تبدیل تصویر به OBJ (روش نقشه ارتفاع خطی) |
| پرداخت | شبیه‌سازی / بله | شبیه‌سازی داخلی (برای تست) یا اتصال به کیف پول بله |
| پیام‌رسان | بله (ربات) | دریافت فاکتور و اطلاع‌رسانی به کاربر (در صورت فعال‌سازی واقعی) |

---

## 🧪 روش نهایی انتخاب‌شده: **مجسمه برجسته (Relief Sculpture)**

فرمول پایه:  
`Z(x,y) = شدت روشنایی پیکسل × ضریب ارتفاع`  
با مثلث‌بندی منظم و انتخاب کوتاه‌ترین قطر.  
**بدون نیاز به scipy**، فقط `numpy` و `Pillow`.  
خروجی صفحه‌ای تخت با برجستگی – قابل چاپ سه‌بعدی.

---

## 🚀 راه‌اندازی سریع (Termux / Vercel)

```bash
# 1. نصب پیش‌نیازها
pkg update && pkg upgrade -y
pkg install python python-pip nodejs
pip install numpy Pillow

# 2. کلون و نصب وابستگی‌ها
git clone https://github.com/tetrashop/bale_3d_bot.git
cd bale_3d_bot
npm install
npm install three

# 3. تنظیم متغیرهای محیطی (اختیاری)
cp .env.example .env.local
# در صورت نیاز توکن‌های واقعی را وارد کنید

# 4. اجرا
npx next dev --webpack --port 3000
```

سپس مرورگر را باز کنید: http://localhost:3000

---

💳 پرداخت – حالت شبیه‌سازی (پیش‌فرض)

در .env.local مقدار SIMULATE_PAYMENT=true قرار دارد. در این حالت بدون نیاز به توکن واقعی، بلافاصله پس از کلیک روی «پرداخت و دانلود» لینک OBJ نمایش داده می‌شود. برای پرداخت واقعی بله باید SIMULATE_PAYMENT=false و BOT_TOKEN و WALLET_ID معتبر تنظیم گردد و Webhook با zrok راه‌اندازی شود.

---

🎨 پیش‌نمایش سه‌بعدی

پس از تبدیل، مدل OBJ در یک صحنه Three.js نمایش داده می‌شود. کاربر می‌تواند آن را بچرخاند و ببیند.

---

📦 ساختار نهایی پروژه

```
bale_3d_bot/
├── pages/
│   ├── api/
│   │   ├── upload.js
│   │   ├── create-payment.js
│   │   ├── check-payment.js
│   │   └── download.js
│   └── index.js
├── public/
│   └── models/
├── lib/
│   └── state.js
├── engine_3d.py
├── next.config.js
├── .env.local
├── .gitignore
└── README.md
