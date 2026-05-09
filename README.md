# تبدیل تصاویر دو بعدی به مدل‌های سه‌بعدی  
## مستند کامل پروژه – نسخه نهایی (Relief Sculpture + شبیه‌سازی پرداخت + Flask API)

**نویسنده:** رامین اجلال  
**آخرین بروزرسانی:** اردیبهشت ۱۴۰۴  
**مخزن:** [github.com/tetrashop/bale_3d_bot](https://github.com/tetrashop/bale_3d_bot)

---

## 📌 فهرست مطالب

1. [معماری نهایی سیستم](#معماری-نهایی-سیستم)
2. [روش انتخاب‌شده: مجسمه برجسته](#روش-انتخابشده-مجسمه-برجسته)
3. [راه‌اندازی سریع (اجرای محلی)](#راهاندازی-سریع-اجرای-محلی)
   - [الف) روش مبتنی بر `engine_3d.py` (مستقیم)](#الف-روش-مبتنی-بر-engine_3dpy-مستقیم)
   - [ب) روش مبتنی بر Flask API (پایدارتر)](#ب-روش-مبتنی-بر-flask-api-پایدارتر)
4. [شبیه‌سازی پرداخت (تست آفلاین)](#شبیهسازی-پرداخت-تست-آفلاین)
5. [استقرار روی Vercel (حالت تولید)](#استقرار-روی-vercel-حالت-تولید)
6. [عیب‌یابی و مشکلات رایج](#عیبیابی-و-مشکلات-رایج)
7. [ساختار نهایی پروژه](#ساختار-نهایی-پروژه)

---

## 🧠 معماری نهایی سیستم

| لایه | فناوری | وظیفه |
|------|--------|--------|
| Frontend | Next.js + React | آپلود تصویر، نمایش پیش‌نمایش Three.js، فرم پرداخت |
| Backend API (Node.js) | Next.js API Routes | دریافت تصویر، ارتباط با موتور پایتون |
| موتور تبدیل (پایدار) | Python + Flask | `api_server.py` که `engine_3d.py` را فراخوانی می‌کند |
| موتور تبدیل (بدون Flask) | Python + `engine_3d.py` | تبدیل مستقیم تصویر به OBJ (بین‌المللی) |
| پرداخت | شبیه‌سازی داخلی / کیف پول بله | تصویر‌سازی برای تست یا اتصال واقعی |
| پیام‌رسان | بله (ربات) | اطلاع‌رسانی (اختیاری) |

---

## 🧪 روش انتخاب‌شده: **مجسمه برجسته (Relief Sculpture)**

فرمول پایه:
```

Z(x,y) = شدت روشنایی پیکسل × ضریب ارتفاع

```
به همراه:
- میانگین سه کانال RGB → شدت روشنایی
- فیلتر میانه ۳×۳ (کاهش نویز)
- مثلث‌بندی شبکه منظم با انتخاب کوتاه‌ترین قطر
- تصحیح نرمال‌ها با مساحت علامت‌دار در XY
- **بدون نیاز به scipy**، فقط `numpy` و `Pillow`
- خروجی OBJ صفحه‌ای تخت با برجستگی – قابل چاپ سه‌بعدی

---

## 🚀 راه‌اندازی سریع (اجرای محلی)

### الف) روش مبتنی بر `engine_3d.py` (مستقیم)

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
cp .env.example .env.local    # در صورت وجود
echo "SIMULATE_PAYMENT=true" >> .env.local

# 4. اجرا
npx next dev --webpack --port 3000
```

سپس مرورگر را باز کنید: http://localhost:3000

ب) روش مبتنی بر Flask API (پایدارتر – پیشنهاد شده)

این روش از یک API مستقل پایتون استفاده می‌کند که پایدارتر است و با خطای SIGTERM مواجه نمی‌شود.

ترمینال ۱ – اجرای سرویس Flask:

```bash
cd ~/bale_3d_bot
python3 api_server.py
```

خروجی:

```
* Running on http://0.0.0.0:5000
* Running on http://192.168.1.101:5000
```

ترمینال ۲ – اجرای Next.js:

```bash
cd ~/bale_3d_bot
npm run dev
```

تست مستقیم API با curl:

```bash
curl -X POST -F "file=@test_image.jpg" http://192.168.1.101:5000/process --output model.obj
```

نکته: در مرورگر گوشی از آدرس http://192.168.1.101:3000 استفاده کنید.

---

💳 شبیه‌سازی پرداخت (تست آفلاین)

در فایل .env.local مقدار زیر را قرار دهید:

```
SIMULATE_PAYMENT=true
```

در این حالت دکمه «پرداخت و دانلود» بدون نیاز به هیچ توکن واقعی، بلافاصله لینک دانلود OBJ را نشان می‌دهد. برای پرداخت واقعی بله باید SIMULATE_PAYMENT=false و BOT_TOKEN و WALLET_ID معتبر تنظیم گردد.

---

🌐 استقرار روی Vercel (حالت تولید)

برای استقرار در بستر ابری (بدون نیاز به سرور محلی) کافی است پروژه را به مخزن گیت‌هاب پوش کرده و در Vercel مستقر کنید.
تنظیمات vercel.json و pages/api/process.py به گونه‌ای است که از توابع پایتون (serverless) استفاده می‌کند.

```bash
# پس از اطمینان از کدهای نهایی
git add .
git commit -m "Deploy ready"
git push origin main
```

سپس در داشبورد Vercel:

· پروژه جدید ← Import از مخزن tetrashop/bale-3d-bot
· Set Environment Variables: SIMULATE_PAYMENT=true (اختیاری)
· Deploy

پس از استقرار، آدرسی مثل https://bale-3d-bot.vercel.app در اختیار شماست.

---

🛠️ عیب‌یابی و مشکلات رایج

خطا راه‌حل
Module not found: multer npm install multer
Python error: SIGTERM از روش Flask API استفاده کنید (اجرای جداگانه)
Failed to fetch در مرورگر در pages/api/uploadImage.js آدرس Flask را به IP شبکه تغییر دهید
Address already in use پورت ۵۰۰۰ pkill -f api_server.py سپس دوباره اجرا کنید
Vercel دیپلوی نمی‌شود (Timeout) maxDuration در vercel.json را افزایش دهید یا max_res را کاهش دهید
اتصال به Vercel از Termux قطع است از یک دستگاه دیگر با اینترنت آزاد استفاده کنید

---

📦 ساختار نهایی پروژه

```
bale_3d_bot/
├── pages/
│   ├── api/
│   │   ├── uploadImage.js      ← فراخوانی محلی `engine_3d.py` یا Flask
│   │   ├── process.py          ← تابع پایتون برای Vercel
│   │   ├── payment.js          ← درگاه پرداخت (شبیه‌سازی یا واقعی)
│   │   └── download.js         ← دریافت فایل OBJ پس از پرداخت
│   └── index.js                ← صفحه اصلی با Three.js
├── public/
│   └── models/                 ← محل ذخیره فایل OBJ
├── lib/
│   └── state.js                ← مدیریت وضعیت پرداخت
├── engine_3d.py                ← موتور اصلی تبدیل
├── api_server.py               ← سرویس HTTP پایدار با Flask
├── next.config.js
├── vercel.json                 ← تنظیمات استقرار
├── requirements.txt            ← وابستگی‌های پایتون (برای Vercel)
├── .env.local                  ← متغیرهای محیطی (اختیاری)
└── README.md
```

---

✅ جمع‌بندی

· موتور تبدیل پایدار و بدون وابستگی‌های سنگین است.
· دو روش اجرا: مستقیم (engine_3d.py) و از طریق Flask API (پیشنهادی برای جلوگیری از کرش).
· پرداخت به صورت شبیه‌سازی (برای تست) یا واقعی (در صورت تنظیم توکن) کار می‌کند.
· استقرار ابری روی Vercel با توابع پایتون امکان‌پذیر است (نیاز به اینترنت آزاد).

پروژه کاملاً عملیاتی و آماده‌ی استفاده است. 🚀

نویسنده: رامین اجلال
ارتباط: ramin.edjlal@example.com
آخرین بروزرسانی: اردیبهشت ۱۴۰۴
