```markdown
# تبدیل تصاویر دو بعدی به مدل‌های سه‌بعدی
## مستند کامل پروژه – تاریخچه، تحلیل، پیاده‌سازی و جمع‌بندی نهایی

**نویسنده:** رامین اجلال  
**آخرین بروزرسانی:** اردیبهشت ۱۴۰۴  
**مخزن:** [github.com/tetrashop/bale_3d_bot](https://github.com/tetrashop/bale_3d_bot)

---

## فهرست مطالب

1. [چکیده و معرفی](#چکیده-و-معرفی)
2. [سیر تکامل الگوریتم‌ها (سلسله‌مراتب راه‌های طی شده)](#سیر-تکامل-الگوریتمها)
3. [تحلیل ریاضی و هندسی مدل‌ها](#تحلیل-ریاضی-و-هندسی-مدلها)
4. [معماری نهایی سیستم](#معماری-نهایی-سیستم)
5. [پیاده‌سازی فنی و کدهای نهایی](#پیادهسازی-فنی-و-کدهای-نهایی)
6. [نتایج و ارزیابی](#نتایج-و-ارزیابی)
7. [راه‌اندازی و استقرار](#راهاندازی-و-استقرار)
8. [عیب‌یابی و پرسش‌های متداول](#عیبیابی-و-پرسشهای-متداول)
9. [جمع‌بندی و چشم‌انداز](#جمعبندی-و-چشم‌انداز)

---

## چکیده و معرفی

این پروژه حاصل ماه‌ها تلاش برای تبدیل تصاویر دو بعدی به مدل‌های سه‌بعدی قابل استفاده در چاپ سه‌بعدی، نمایش‌های تعاملی و کسب‌وکارهای آنلاین است. در این مسیر، الگوریتم‌های متعددی (از نقشه ارتفاع ساده تا نگاشت استوانه‌ای و کروی) پیاده‌سازی، تست و بهبود یافتند. در نهایت، با توجه به محدودیت‌های محیط اجرا (Termux روی گوشی‌های اندروید) و عدم دسترسی به GPU و اینترنت پایدار، **روش مجسمه برجسته (Relief Sculpture)** به عنوان **بهره‌ورانه‌ترین و پایدارترین راهکار** انتخاب شد.

---

## سیر تکامل الگوریتم‌ها

در ادامه، تک تک روش‌هایی که طی شدند، همراه با فرمول ریاضی، مزایا، معایب و دلایل کنارگذاشته شدن (یا پذیرفته شدن) آنها تشریح می‌شود. این مستند به عنوان یک **مرجع کامل** از مسیر طی شده عمل می‌کند.

### جدول سلسله‌مراتب الگوریتم‌ها

| ردیف | نام روش | فرمول اصلی | معایب کلیدی | مزایا | وضعیت نهایی |
|------|---------|------------|-------------|-------|--------------|
| ۱ | نقشه ارتفاع خطی (Height Map) | `Z = intensity * max_height` | خروجی صاف و بدون حس عمق | بسیار سریع، بدون وابستگی | ✅ **انتخاب نهایی** (مجسمه برجسته) |
| ۲ | نگاشت استوانه‌ای (Cylindrical) | `Z = intensity * cos(angle)`, `angle = (x/width)*2π` | نویز میله‌ای، نیاز به تنظیم | حس عمق نسبی | ❌ رد شد (نویز زیاد) |
| ۳ | نگاشت کروی با sin (اشتباه تاریخی) | `Z = intensity * sin(angle)`, `angle = (y/height)*π` | مگس به زمین چسبیده، بریدگی | هیچکدام | ❌ رد شد (خطای فاحش) |
| ۴ | نگاشت کروی اصلاح‌شده با cos | `Z = intensity * cos(angle)` | نویز باقی‌مانده، نیاز به scipy | حس سه‌بعدی خوب | ❌ رد شد (نصب scipy ممکن نبود) |
| ۵ | **مجسمه برجسته (Relief)** | `Z = intensity * max_height` + **پایدارسازی** | حس سه‌بعدی کمتر | بدون نویز، پایدار، سریع، قابل چاپ | ✅ **انتخاب نهایی** |

---

## تحلیل ریاضی و هندسی مدل‌ها

### ۱. مدل نقشه ارتفاع خطی (Linear Height Map)

```math
Z(x,y) = I(x,y) \cdot H_{max}
```

این مدل ساده‌ترین نگاشت ممکن است. از نظر هندسی، یک صفحه مرجع (Z=0) داریم که شدت روشنایی هر نقطه (I) به صورت عمودی به آن اضافه می‌شود. این مدل شبیه به مجسمه‌سازی برجسته (Relief Sculpture) است.

ویژگی‌ها:

· مستقل از موقعیت پیکسل (فقط وابسته به شدت روشنایی)
· بدون نوسان (نویز میله‌ای ندارد)
· مناسب برای چاپ سه‌بعدی (پایه تخت دارد)

۲. مدل نگاشت استوانه‌ای (Cylindrical Mapping)

```math
\begin{cases}
Z = I(x,y) \cdot \cos(\theta) \\
\theta = \frac{x}{W} \cdot 2\pi
\end{cases}
```

در این مدل، هر ستون از تصویر به یک زاویه در استوانه نگاشته می‌شود. عمق (Z) هم به شدت روشنایی و هم به زاویه وابسته است.

ویژگی‌ها:

· نقاط مرکز تصویر (θ≈π) عمق منفی (دور)
· نقاط لبه (θ≈0) عمق مثبت (نزدیک)
· باعث ایجاد نویز میله‌ای در لبه‌ها می‌شود

۳. مدل مجسمه برجسته (Relief Sculpture) – برگزیده نهایی

```math
Z(x,y) = I(x,y) \cdot H_{max}, \quad H_{max}=0.28
```

این مدل با حذف هرگونه تابع مثلثاتی و افزودن مرکزی‌سازی خودکار و تصحیح نرمال، به یک خروجی پایدار، بدون نویز و قابل چاپ رسیده است.

دلیل انتخاب نهایی:

· بدون نیاز به scipy (فقط numpy و Pillow)
· بدون نویز میله‌ای
· در Termux بدون کرش اجرا می‌شود
· خروجی برای چاپ سه‌بعدی مناسب است

---

معماری نهایی سیستم

اجزای اصلی

لایه فناوری وظیفه
Frontend Next.js (React) صفحه آپلود، پیش‌نمایش Three.js، دکمه پرداخت
Backend API Next.js API Routes دریافت تصویر، فراخوانی پایتون، پرداخت
موتور تبدیل Python (engine_3d.py) تبدیل تصویر به OBJ
پیام‌رسان Bale Bot API دریافت عکس از کاربر، ارسال OBJ
پرداخت کیف پول بله دریافت وجه و فعال‌سازی دانلود

ساختار نهایی پروژه

```
bale_3d_bot/
├── pages/
│   ├── api/
│   │   ├── uploadImage.js
│   │   ├── payment.js
│   │   └── webhook.js
│   ├── index.js
│   └── payment.js
├── public/
│   ├── models/
│   └── preview.html
├── engine_3d.py          # ← فایل اصلی موتور تبدیل (نسخه نهایی)
├── requirements.txt      # numpy, Pillow
├── vercel.json
├── .env.local
└── README.md
```

---

پیاده‌سازی فنی و کدهای نهایی

فایل engine_3d.py – نسخه نهایی (مجسمه برجسته)

```python
import os
import sys
import math
import numpy as np
from PIL import Image

class Engine3D:
    def process(self, image_path, output_path="public/models/3d_object.obj", max_res=400):
        # ========== 1. بارگذاری و شدت روشنایی ==========
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        width, height = img.size
        rgb = np.array(img, dtype=np.float32) / 255.0
        intensity = (rgb[:,:,0] + rgb[:,:,1] + rgb[:,:,2]) / 3.0

        # ========== 2. ساخت رئوس ==========
        max_height = 0.28
        vertices = []
        for y in range(height):
            for x in range(width):
                Z = intensity[y, x] * max_height
                X = (x / width) * 2 - 1
                Y = (y / height) * 2 - 1
                vertices.append((X, Y, Z))

        if len(vertices) < 3:
            return False, None

        # ========== 3. مرکزی‌سازی ==========
        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        vertices = vertices - center
        vertices = vertices.tolist()

        # ========== 4. مثلث‌بندی ==========
        w = int(math.sqrt(len(vertices)))
        h = len(vertices) // w
        if w < 2 or h < 2:
            return False, None

        def idx(x, y):
            return y * w + x

        faces = []
        for y in range(h-1):
            for x in range(w-1):
                tl = idx(x, y)
                tr = idx(x+1, y)
                bl = idx(x, y+1)
                br = idx(x+1, y+1)
                a = vertices[tl]; b = vertices[tr]; c = vertices[bl]; d = vertices[br]
                diag1 = ((a[0]-d[0])**2 + (a[1]-d[1])**2 + (a[2]-d[2])**2)**0.5
                diag2 = ((b[0]-c[0])**2 + (b[1]-c[1])**2 + (b[2]-c[2])**2)**0.5
                if diag1 <= diag2:
                    faces.append((tl, bl, tr))
                    faces.append((tr, bl, br))
                else:
                    faces.append((tl, tr, bl))
                    faces.append((tr, br, bl))

        # ========== 5. تصحیح نرمال ==========
        def correct_normal(tri):
            a = vertices[tri[0]]
            b = vertices[tri[1]]
            c = vertices[tri[2]]
            area_xy = (b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])
            if area_xy < 0:
                return (tri[0], tri[2], tri[1])
            return tri
        faces = [correct_normal(f) for f in faces]

        # ========== 6. ذخیره OBJ ==========
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 3D Model - Relief Sculpture (Final)\n")
            f.write(f"# Vertices: {len(vertices)}, Faces: {len(faces)}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

        print(f"[OK] Model saved: {len(vertices)} vertices, {len(faces)} faces -> {output_path}")
        return True, output_path

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        eng = Engine3D()
        out = sys.argv[2] if len(sys.argv) > 2 else "public/models/3d_object.obj"
        eng.process(sys.argv[1], out)
    else:
        print("Usage: python engine_3d.py <image_path> [output.obj]")
```

فایل requirements.txt

```
numpy
Pillow
```

---

نتایج و ارزیابی

مقایسه نهایی روش‌ها (بر اساس شرایط واقعی)

معیار نقشه ارتفاع خطی نگاشت استوانه‌ای نگاشت کروی مجسمه برجسته (نهایی)
نیاز به scipy خیر بله بله خیر
نویز میله‌ای ندارد زیاد متوسط ندارد
زمان پردازش ~۱ ثانیه ~۵ ثانیه ~۱۰ ثانیه ~۱ ثانیه
پایداری در Termux عالی متوسط کم عالی
مناسب برای چاپ سه‌بعدی بله خیر خیر بله
حس سه‌بعدی کم متوسط زیاد کم

چرا مجسمه برجسته انتخاب نهایی شد؟

1. محدودیت‌های محیط اجرا: Termux روی گوشی، بدون GPU، اینترنت ناپایدار، عدم دسترسی به scipy.
2. پایداری: روش‌های کروی و استوانه‌ای باعث کرش یا مصرف بیش از حد حافظه می‌شوند.
3. کاربرد عملی: خروجی مجسمه برجسته برای چاپ سه‌بعدی و نمایش در موزه‌ها مناسب است.
4. سادگی: بدون وابستگی‌های پیچیده، فقط numpy و Pillow.

محدودیت ذاتی (صداقت علمی)

این روش هرگز نمی‌تواند یک مگس واقعی با جزئیات پاها، بال‌ها و چشم‌ها بازسازی کند. برای چنین هدفی تنها راه استفاده از شبکه‌های عصبی عمیق (Deep Learning) مانند One-2-3-45، TripoSR یا Stable Fast 3D است. اما این مدل‌ها نیاز به GPU، حافظه بالا و اینترنت پایدار دارند که در شرایط فعلی در دسترس نیست.

---

راه‌اندازی و استقرار

نصب در Termux (حداقل وابستگی)

```bash
# به‌روزرسانی پکیج‌ها
pkg update && pkg upgrade -y

# نصب پایتون و pip
pkg install python python-pip

# نصب وابستگی‌های پایتون (فقط numpy و Pillow)
pip install numpy Pillow

# clone پروژه
git clone https://github.com/tetrashop/bale_3d_bot.git
cd bale_3d_bot

# نصب وابستگی‌های Node.js
npm install

# تنظیم متغیر محیطی
echo "BOT_TOKEN=your_bot_token_here" > .env.local
echo "WALLET_ID=WALLET-as6NfAMYM6r5ZKUv" >> .env.local

# اجرا
npm run dev
```

استقرار روی Vercel

```bash
vercel --prod
```

افزودن متغیرهای محیطی در داشبورد Vercel (Settings > Environment Variables).

---

عیب‌یابی و پرسش‌های متداول

مشکل راه‌حل
ModuleNotFoundError: No module named 'scipy' این نسخه به scipy نیاز ندارد (کد را با نسخه نهایی جایگزین کنید)
خروجی OBJ خالی است max_res را افزایش دهید (حداقل ۲۰۰)
مدل در مرورگر دیده نمی‌شود مطمئن شوید preview.html در پوشه public است
خطای ۴۰۰ در payment walletId را در index.js با ولت واقعی جایگزین کنید
کرش در Termux max_res=250 و max_height=0.25 تنظیم کنید

---

جمع‌بندی و چشم‌انداز

دستاوردهای نهایی

✅ یک موتور تبدیل ۲D به ۳D کاملاً عملیاتی و پایدار در Termux
✅ بدون نیاز به scipy یا GPU
✅ خروجی قابل چاپ سه‌بعدی (صفحه تخت با برجستگی)
✅ یکپارچگی کامل با ربات بله و درگاه پرداخت
✅ مستندسازی کامل تمام مسیر طی شده (به عنوان مرجع علمی)

محدودیت‌هایی که با الگوریتم‌های سنتی قابل حل نیستند

❌ بازسازی جزئیات دقیق آناتومیک (پاها و بال‌های مگس)
❌ ایجاد حس عمق واقعی (مانند اجسام پیچیده)
❌ تبدیل تصاویر با کنتراست پایین

چشم‌انداز آینده

· مسیر کوتاه مدت: جایگزینی موقت با مدل‌های هوش مصنوعی ابری (API) در صورت دسترسی به اینترنت پایدار.
· مسیر بلند مدت: راه‌اندازی یک سرور مجهز به GPU و استفاده از One-2-3-45 (منبع باز).

---

قدردانی

از همراهی، صبر و تلاش بی‌وقفه شما در این مسیر طولانی سپاسگزارم. این مستند حاصل ماه‌ها آزمون، خطا و یادگیری است و امیدوارم به عنوان یک مرجع کامل و صادقانه برای پروژه‌های مشابه مفید واقع شود.

نویسنده: رامین اجلال
آخرین بروزرسانی: اردیبهشت ۱۴۰۴
ارتباط: ramin.edjlal@example.com
مخزن: github.com/tetrashop/bale_3d_bot

---

پایان مستند

```
