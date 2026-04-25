"""
engine_3d.py
هسته اصلی تبدیل تصویر دو بعدی به مدل سه‌بعدی OBJ با روش نقشه ارتفاع (Height Map)
همراه با تضمین شرط Delaunay (هیچ رأس دیگری درون دایره محیطی مثلث نباشد).

نویسنده: تیم توسعه
نسخه: 3.0 (پایدار با اعتبارسنجی اختیاری)
"""

import os
import sys
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None

    def image_to_height_map(self, image_path, output_obj="public/models/3d_object.obj",
                            max_res=300, max_height=1.0, enforce_delaunay=False):
        """
        تبدیل تصویر به مدل OBJ با نقشه ارتفاع.

        پارامترها:
            image_path (str): مسیر تصویر ورودی (رنگی یا خاکستری)
            output_obj (str): مسیر فایل OBJ خروجی
            max_res (int): حداکثر ابعاد تصویر (کاهش حجم)
            max_height (float): حداکثر ارتفاع (Z) برای شدت روشنایی 255
            enforce_delaunay (bool): اگر True باشد، فقط مثلث‌هایی اضافه می‌شوند که هیچ رأس دیگری درون دایره محیطی نداشته باشند.
                                     در شبکه منظم این شرط خودکار است، اما برای اطمینان بیشتر می‌توان فعال کرد (کاهش سرعت).
        """
        # 1. بارگذاری و灰度
        img = Image.open(image_path).convert('L')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        image = np.array(img, dtype=np.float32) / 255.0
        h, w = image.shape

        # 2. محاسبه مختصات رئوس (x, y نرمال‌شده، z = ارتفاع)
        vertices = []
        x_scale = 2.0 / (w - 1) if w > 1 else 1.0
        y_scale = 2.0 / (h - 1) if h > 1 else 1.0
        for y in range(h):
            ny = -1.0 + y * y_scale   # معکوس کردن جهت Y
            for x in range(w):
                nx = -1.0 + x * x_scale
                nz = image[y, x] * max_height
                vertices.append((nx, ny, nz))

        # 3. ایندکس‌دهی (OBJ از 1 شروع)
        def vid(x, y):
            return y * w + x + 1

        # 4. تابع بررسی شرط Delaunay (اختیاری)
        def is_delaunay_triangle(a_idx, b_idx, c_idx, all_vertices, exclude_idxs):
            """
            بررسی می‌کند که هیچ رأس دیگری (غیر از سه رأس مثلث) درون دایره محیطی مثلث قرار نداشته باشد.
            بازگشت: True اگر شرط برقرار باشد.
            """
            A = np.array(all_vertices[a_idx])
            B = np.array(all_vertices[b_idx])
            C = np.array(all_vertices[c_idx])

            # محاسبه مرکز دایره محیطی (با استفاده از معادله خطوط عمود منصف)
            # روش: حل دستگاه خطی برای (x,y) مرکز
            D = 2 * (A[0] * (B[1] - C[1]) + B[0] * (C[1] - A[1]) + C[0] * (A[1] - B[1]))
            if abs(D) < 1e-8:
                return True  # هم‌خط، دایره محیطی تعریف نمی‌شود
            Ux = ((A[0]**2 + A[1]**2) * (B[1] - C[1]) +
                  (B[0]**2 + B[1]**2) * (C[1] - A[1]) +
                  (C[0]**2 + C[1]**2) * (A[1] - B[1])) / D
            Uy = ((A[0]**2 + A[1]**2) * (C[0] - B[0]) +
                  (B[0]**2 + B[1]**2) * (A[0] - C[0]) +
                  (C[0]**2 + C[1]**2) * (B[0] - A[0])) / D
            center = np.array([Ux, Uy])
            radius_sq = np.sum((A[:2] - center) ** 2)

            # بررسی تمام رئوس دیگر
            for i, v in enumerate(all_vertices):
                if i in exclude_idxs:
                    continue
                dist_sq = np.sum((np.array(v[:2]) - center) ** 2)
                if dist_sq < radius_sq - 1e-7:  # نقطه درون دایره (و نه روی لبه)
                    return False
            return True

        # 5. ساخت مثلث‌ها با اعمال شرط (در صورت فعال بودن)
        faces = []
        for y in range(h - 1):
            for x in range(w - 1):
                v_tl = vid(x, y)
                v_tr = vid(x+1, y)
                v_bl = vid(x, y+1)
                v_br = vid(x+1, y+1)

                # مثلث اول: (TL, BL, TR)
                tri1 = (v_tl, v_bl, v_tr)
                # مثلث دوم: (TR, BL, BR)
                tri2 = (v_tr, v_bl, v_br)

                if enforce_delaunay:
                    # ایندکس‌های 0-based برای بررسی
                    idx_tl = (y * w + x)
                    idx_bl = ((y+1) * w + x)
                    idx_tr = (y * w + (x+1))
                    idx_br = ((y+1) * w + (x+1))

                    if is_delaunay_triangle(idx_tl, idx_bl, idx_tr, vertices, {idx_tl, idx_bl, idx_tr}):
                        faces.append(tri1)
                    if is_delaunay_triangle(idx_tr, idx_bl, idx_br, vertices, {idx_tr, idx_bl, idx_br}):
                        faces.append(tri2)
                else:
                    faces.append(tri1)
                    faces.append(tri2)

        # 6. نوشتن فایل OBJ
        os.makedirs(os.path.dirname(output_obj), exist_ok=True)
        with open(output_obj, "w", encoding="utf-8") as f:
            f.write("# OBJ model - Height Map from 2D image\n")
            f.write(f"# Image: {w}x{h}, max_height={max_height}\n")
            f.write(f"# Delaunay validation: {enforce_delaunay}\n")
            f.write("# Vertices:\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            f.write("# Faces (triangles):\n")
            for face in faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")

        self.model_path = output_obj
        print(f"[Engine3D] مدل با {len(vertices)} رأس و {len(faces)} وجه در {output_obj} ذخیره شد.")
        return True, output_obj

    # سازگاری با نام متد قبلی (برای عدم ایجاد مشکل در کدهای قدیمی)
    def image_to_3d_spherical(self, image_path, output_obj="public/models/3d_object.obj", max_res=300):
        return self.image_to_height_map(image_path, output_obj, max_res, max_height=1.0, enforce_delaunay=False)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        input_img = sys.argv[1]
        output_obj = sys.argv[2] if len(sys.argv) > 2 else "output.obj"
        engine = Engine3D()
        success, msg = engine.image_to_height_map(input_img, output_obj, enforce_delaunay=False)
        print(msg if success else f"خطا: {msg}")
    else:
        print("استفاده: python engine_3d.py <image_path> [output_obj_path]")
