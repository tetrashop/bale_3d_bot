import os
import sys
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None
        self.vertices = []

    def image_to_3d_spherical(self, image_path, output_obj="public/models/3d_object.obj", max_res=300):
        # بارگذاری تصویر و تبدیل به خاکستری
        img = Image.open(image_path).convert("L")
        img.thumbnail((max_res, max_res), Image.LANCZOS)
        image = np.array(img)

        h, w = image.shape
        cx, cy = w / 2, h / 2
        max_r = np.sqrt(cx ** 2 + cy ** 2)

        self.vertices = []
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy

                # محاسبه مختصات زاویه‌ای کروی
                theta = (dx / max_r) * np.pi       # افقی [-π, π]
                phi = (dy / max_r) * (np.pi / 2)  # عمودی [-π/2, π/2]

                intensity = image[y, x] / 255.0    # نور نرمال شده

                r = intensity                     # ارتفاع برابر شدت نور

                # تبدیل به مختصات کارتزین
                X = r * np.sin(phi) * np.cos(theta)
                Y = r * np.sin(phi) * np.sin(theta)
                Z = r * np.cos(phi)

                self.vertices.append((X, Y, Z))

        def vid(x_, y_):
            # تبدیل اندیس 2 بعدی به اندیس 1-مبنایی برای OBJ
            return y_ * w + x_ + 1

        def is_valid_triangle(v1, v2, v3, axis=np.array([0,0,1]), angle_threshold_deg=10):
            # چک صحت شکل مثلث از نظر نرمال جهت جلوگیری از مثلث‌های افتاده یا نامناسب
            a = np.array(v2) - np.array(v1)
            b = np.array(v3) - np.array(v1)
            n = np.cross(a, b)
            norm_n = np.linalg.norm(n)
            if norm_n < 1e-8:
                return False
            n /= norm_n
            axis = axis / np.linalg.norm(axis)
            angle = np.arccos(np.clip(np.dot(n, axis), -1.0, 1.0))
            angle_deg = np.degrees(angle)
            # حذف مثلث هایی که خیلی عمود یا معکوس جهت محور z باشند
            return not (angle_deg < angle_threshold_deg or angle_deg > (180 - angle_threshold_deg))

        faces = []
        for y in range(h - 1):
            for x in range(w - 1):
                v1 = vid(x, y)
                v2 = vid(x + 1, y)
                v3 = vid(x, y + 1)
                v4 = vid(x + 1, y + 1)

                if is_valid_triangle(self.vertices[v1 - 1], self.vertices[v2 - 1], self.vertices[v3 - 1]):
                    faces.append((v1, v2, v3))
                if is_valid_triangle(self.vertices[v3 - 1], self.vertices[v2 - 1], self.vertices[v4 - 1]):
                    faces.append((v3, v2, v4))

        # اطمینان از وجود پوشه خروجی
        os.makedirs(os.path.dirname(output_obj), exist_ok=True)

        # نوشتن فایل OBJ سالم
        with open(output_obj, "w") as f:
            f.write("# OBJ model with lighting depth and valid triangles\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")

        self.model_path = output_obj
        print(f"مدل سه‌بعدی در فایل {output_obj} ذخیره شد.")
        return True, output_obj


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python engine_3d.py <input_image_path> <output_obj_path>")
        sys.exit(1)

    input_image_path = sys.argv[1]
    output_obj_path = sys.argv[2]

    engine = Engine3D()
    engine.image_to_3d_spherical(input_image_path, output_obj_path)
