import sys
import os
import logging

sys.path.append("..")  # مسیر پروژه برای import

from engine_3d import Engine3D

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

class PaymentManagerMock:
    def process_payment(self, amount):
        logger.info(f"پرداخت شبیه‌سازی شده: مقدار {amount}")
        # اینجا می‌توانی منطق واقعی پرداخت را جایگزین کنی
        return True

def test_model_generation():
    engine = Engine3D()
    input_image = "test_image.jpg"
    if not os.path.exists(input_image):
        logger.error(f"تصویر ورودی موجود نیست: {input_image}")
        return None
    success, filename = engine.generate_model_offline(input_image, "test_model.obj")
    if success:
        logger.info(f"مدل آفلاین ساخته شد: {filename}")
    else:
        logger.error(f"خطا در ساخت مدل: {filename}")
        return None
    loaded = engine.load_model()
    if loaded:
        logger.info(f"مدل 3D بارگذاری شد: {engine.model_path}")
        return engine.model_path
    else:
        logger.error("بارگذاری مدل سه‌بعدی موفق نبود")
        return None

def test_payment():
    pay = PaymentManagerMock()
    if pay.process_payment(10):
        logger.info("پرداخت موفقیت‌آمیز بود")
        return True
    logger.error("پرداخت ناموفق بود")
    return False

def test_download_model(model_path):
    if model_path and os.path.exists(model_path) and os.path.getsize(model_path) > 0:
        logger.info(f"دانلود مدل موفق: فایل موجود و خوانا است: {model_path}")
        return True
    else:
        logger.error(f"دانلود مدل ناموفق: فایل موجود نیست یا خالی است: {model_path}")
        return False

if __name__ == "__main__":
    logger.info("شروع کل تست‌ها")

    model_path = test_model_generation()
    if model_path:
        if test_payment():
            test_download_model(model_path)

    logger.info("پایان تست‌ها")
