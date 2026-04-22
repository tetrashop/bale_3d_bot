import os
import shutil
import time
from db import update_job
from config import OUTPUT_DIR
def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    def process_file(job_id, input_path):
        """
        پردازش ساده و قابل اجرا در Termux:
            - فایل ورودی را به output کپی میکند
            - یک گزارش متنی هم کنار آن میسازد
            """
            ensure_dirs()
            if not os.path.isfile(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
                update_job(job_id, status="processing", error=None)
                base_name = os.path.basename(input_path)
                name, ext = os.path.splitext(base_name)
                output_file = os.path.join(OUTPUT_DIR, f'{name}_processed{ext if ext else ".bin"}')
                report_file = os.path.join(OUTPUT_DIR, f"{name}_report.txt")
                time.sleep(2)
                shutil.copy2(input_path, output_file)
                file_size = os.path.getsize(output_file)
                report_text = (
                f"Job ID: {job_id}\n"
                f"Input: {input_path}\n"
                f"Output: {output_file}\n"
                f"Size: {file_size} bytes\n"
                f"Status: processed successfully\n"
                )
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report_text)
                    update_job(job_id, status="done", output_path=output_file, error=None)
                    return output_file
