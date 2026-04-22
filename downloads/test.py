import os
import sys
from your_engine3d_module import Engine3D  # نام ماژول واقعیتان را بگذارید
import logging
# تنظیم لاگ برای نمایش خطا و اطلاعات
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
def main():
    image_path = os.path.join("downloads", "658377.jpg")
    output_obj = "model_offline.obj"
    # چک فایل وجود دارد؟
    if not os.path.isfile(image_path):
        logging.error(f"فایل ورودی تصویر یافت نشد: {image_path}")
        sys.exit(1)
        try:
            engine = Engine3D()
            logging.info(f"شروع تولید مدل آفلاین از تصویر: {image_path}")
            obj_file_path = engine.generate_model_offline(image_path, output_obj)
            logging.info(f"مدل سهبعدی با موفقیت ایجاد و ذخیره شد در: {obj_file_path}")
        except Exception as e:
            logging.error(f"خطا در تولید مدل سهبعدی: {e}")
            sys.exit(1)
            if __name__ == "__main__":
                main()
