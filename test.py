import logging
import os
from engine_3d import Engine3D
from error_handler import ErrorHandler

def test_engine_3d(error_handler):
    logger = logging.getLogger("TestEngine3D")
    test_image = "downloads/658377.jpg"
    output_obj = "model_offline.obj"
    test_video = "downloads/sample_video.mp4"  # مسیر ویدیو اصلاح شده

    if not os.path.isfile(test_image):
        logger.error(f"تصویر تست یافت نشد: {test_image}")
        return

    if not os.path.isfile(test_video):
        logger.warning(f"ویدیو نمونه {test_video} یافت نشد. لطفا ویدیوی مناسب داخل فولدر downloads قرار دهید.")

    try:
        engine = Engine3D()
        success, result = engine.generate_model_offline(test_image, output_obj)
        if success:
            error_handler.log_info(f"مدل آفلاین با موفقیت ساخته شد: {result}")

            if engine.load_model():
                data = engine.process_video_to_3d(test_video)
                if data:
                    error_handler.log_info(f"طول داده مدل 3D: {len(data)}")
                else:
                    error_handler.log_warning("ویدیو موجود نیست یا پردازش نشده است.")
            else:
                error_handler.log_warning("بارگذاری مدل نا موفق بود.")
        else:
            error_handler.log_error(f"خطا در ایجاد مدل آفلاین: {result}")
    except Exception as e:
        error_handler.log_error(f"خطا در اجرای تست موتور 3D: {e}")

def main():
    logging.basicConfig(level=logging.INFO)
    error_handler = ErrorHandler()

    error_handler.log_info("شروع تست‌ها")
    test_engine_3d(error_handler)
    error_handler.log_info("تست‌ها پایان یافت")

if __name__ == "__main__":
    main()
