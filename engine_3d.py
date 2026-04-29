import os
import sys
import numpy as np
from PIL import Image
from typing import Tuple, List, Optional

class Engine3D:
    """
    تبدیل تصویر 2D به مدل سه‌بعدی (height map) و ذخیره به فرمت OBJ.
    """
    def __init__(self):
        pass

    @staticmethod
    def _load_and_preprocess(image_path: str, max_res: int) -> np.ndarray:
        """بارگذاری تصویر، تبدیل به grayscale و تغییر ابعاد."""
        img = Image.open(image_path).convert('L')  # L = luminance (grayscale)
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        return np.array(img, dtype=np.float32)  # (height, width)

    @staticmethod
    def _generate_mesh(height_map: np.ndarray, z_scale: float = 0.5) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
        """
        تولید شبکه‌ی منظم مثلثی از نقشه‌ی ارتفاع.
        بازگشت: (رئوس, وجوه) با ایندکس‌های صفر-بیس.
        """
        h, w = height_map.shape
        # ایجاد مختصات x, y نرمالیزه در بازه [-1, 1]
        x_coords = np.linspace(-1, 1, w)
        y_coords = np.linspace(-1, 1, h)
        # تبدیل به شبکه (meshgrid) و بازآرایی
        xv, yv = np.meshgrid(x_coords, y_coords)
        # مقدار z از نقشه‌ی ارتفاع (نرمالیزه در [0,1] سپس مقیاس)
        z_min, z_max = height_map.min(), height_map.max()
        if z_max - z_min < 1e-8:
            z_normalized = np.zeros_like(height_map)
        else:
            z_normalized = (height_map - z_min) / (z_max - z_min)
        z_vals = z_normalized * z_scale

        # ساخت لیست رئوس: هر رأس = (x, y, z)
        vertices = []
        for i in range(h):
            for j in range(w):
                vertices.append((xv[i, j], yv[i, j], z_vals[i, j]))

        # تولید وجوه (دو مثلث در هر سلول از شبکه)
        faces = []
        for i in range(h - 1):
            for j in range(w - 1):
                # ایندکس رئوس چهارگوش: tl, tr, bl, br
                idx = lambda x, y: y * w + x
                tl = idx(j, i)      # top-left
                tr = idx(j+1, i)    # top-right
                bl = idx(j, i+1)    # bottom-left
                br = idx(j+1, i+1)  # bottom-right

                # دو مثلث با قطر کوتاه‌تر (بهبود کیفیت)
                # محاسبه طول قطرها با استفاده از نقاط
                a = np.array(vertices[tl])
                b = np.array(vertices[tr])
                c = np.array(vertices[bl])
                d = np.array(vertices[br])
                diag1 = np.linalg.norm(a - d)
                diag2 = np.linalg.norm(b - c)

                if diag1 <= diag2:
                    faces.append((tl, bl, tr))
                    faces.append((tr, bl, br))
                else:
                    faces.append((tl, tr, bl))
                    faces.append((tr, br, bl))
        return vertices, faces

    @staticmethod
    def _export_obj(vertices: List[Tuple[float, float, float]],
                    faces: List[Tuple[int, int, int]],
                    output_path: str) -> None:
        """ذخیره رئوس و وجوه در فایل OBJ."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 3D Model from height map\n")
            f.write(f"# Vertices: {len(vertices)}, Faces: {len(faces)}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                # OBJ ایندکس از 1 شروع می‌شود
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

    def process(self, image_path: str, output_path: str = "public/models/3d_object.obj",
                max_res: int = 300, z_scale: float = 0.5) -> Tuple[bool, Optional[str]]:
        """
        تبدیل تصویر به مدل OBJ.

        پارامترها:
            image_path: مسیر فایل تصویر ورودی
            output_path: مسیر فایل OBJ خروجی
            max_res: حداکثر ابعاد تصویر (عرض یا ارتفاع)
            z_scale: ضریب مقیاس ارتفاع (بزرگتر = برجستگی بیشتر)

        بازگشت:
            (موفقیت, مسیر خروجی یا None)
        """
        try:
            # 1. بارگذاری و پیش‌پردازش
            height_map = self._load_and_preprocess(image_path, max_res)

            # 2. تولید شبکه مثلثی
            vertices, faces = self._generate_mesh(height_map, z_scale)

            if len(vertices) < 3 or len(faces) == 0:
                print("[ERROR] Not enough vertices/faces to create a mesh.")
                return False, None

            # 3. ذخیره به OBJ
            self._export_obj(vertices, faces, output_path)

            print(f"[SUCCESS] Model saved: {len(vertices)} vertices, {len(faces)} faces -> {output_path}")
            return True, output_path

        except FileNotFoundError:
            print(f"[ERROR] Image file not found: {image_path}")
            return False, None
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False, None


def main():
    if len(sys.argv) < 2:
        print("Usage: python engine_3d.py <image_path> [output.obj] [max_res] [z_scale]")
        print("Example: python engine_3d.py input.jpg output.obj 300 0.7")
        sys.exit(1)

    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "public/models/3d_object.obj"
    max_res = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    z_scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5

    engine = Engine3D()
    success, _ = engine.process(image_path, output_path, max_res, z_scale)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
