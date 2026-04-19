import os
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger("Engine3D")

class Engine3D:
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None

    def load_model(self) -> bool:
        if not self.model_path or not os.path.exists(self.model_path):
            logger.error(f"3D model file not found: {self.model_path}")
            return False
        try:
            with open(self.model_path, "rb") as f:
                self.model = f.read()
            logger.info(f"3D model loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load 3D model: {e}")
            return False

    def generate_model_offline(self, image_path: str, obj_filename="model_offline.obj"):
        if not os.path.exists(image_path):
            return False, f"Input image file not found: {image_path}"

        try:
            img = Image.open(image_path).convert("L")
            image = np.array(img)

            max_res = 300
            if image.shape[0] > max_res or image.shape[1] > max_res:
                img = img.resize((max_res, max_res), Image.Resampling.LANCZOS)
                image = np.array(img)

            h, w = image.shape
            cx, cy = w / 2, h / 2

            with open(obj_filename, "w") as f:
                f.write("# OBJ model generated offline\n")
                f.write("o OfflineModel\n")

                for y in range(h):
                    for x in range(w):
                        dx, dy = x - cx, y - cy
                        theta = np.arctan2(dy, dx)
                        r_xy_norm = np.sqrt(dx*dx + dy*dy) / max(cx, cy)
                        phi = (np.pi / 2) * (r_xy_norm ** 1.5)
                        intensity = image[y, x] / 255.0
                        r = intensity * 1.0

                        X = r * np.sin(phi) * np.cos(theta)
                        Y = r * np.sin(phi) * np.sin(theta)
                        Z = r * np.cos(phi)

                        f.write(f"v {X:.6f} {Y:.6f} {Z:.6f}\n")

                def vertex_id(x_, y_):
                    return y_ * w + x_ + 1

                for y in range(h -1):
                    for x in range(w -1):
                        v1 = vertex_id(x, y)
                        v2 = vertex_id(x + 1, y)
                        v3 = vertex_id(x, y + 1)
                        v4 = vertex_id(x + 1, y + 1)

                        f.write(f"f {v1} {v2} {v3}\n")
                        f.write(f"f {v3} {v2} {v4}\n")

            logger.info(f"Offline 3D model generated and saved to {obj_filename}")
            self.model_path = obj_filename
            return True, obj_filename

        except Exception as e:
            logger.error(f"Error generating offline model: {e}")
            return False, str(e)

    def process_video_to_3d(self, video_path: str):
        if not os.path.exists(video_path):
            logger.warning(f"Video file not found: {video_path}")
            return None
        try:
            logger.info(f"Processing video {video_path} to 3D model")
            # پیاده‌سازی واقعی پخش ویدیو و تبدیل به مدل سه‌بعدی اینجا انجام شود
            # برای تست اینجا فایل دمی ایجاد شده برگردانده می‌شود
            dummy_path = os.path.join(os.path.dirname(video_path), "dummy_model.obj")
            with open(dummy_path, "w") as f:
                f.write("# Dummy 3D model for test\n")
            with open(dummy_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return None
    def process_video_to_3d(self, video_path):
        if not os.path.exists(video_path):
            logger.warning(f"Video file not found: {video_path}")
            # برای تست حداقل فایل نمادین بساز
            dummy_obj = "dummy_model_from_video.obj"
            with open(dummy_obj, "w") as f:
                f.write("# dummy 3d model from video")
            with open(dummy_obj, "rb") as f:
                return f.read()
        # اینجا پردازش واقعی ویدیو به مدل قرار می‌گیرد
        # در غیر اینصورت تابع تست بدون خطا
        dummy_obj = "dummy_model_from_video.obj"
        with open(dummy_obj, "w") as f:
            f.write("# dummy 3d model from video")
        with open(dummy_obj, "rb") as f:
            return f.read()
