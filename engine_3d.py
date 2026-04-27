import os
import sys
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None

    @staticmethod
    def _median_filter(arr, kernel_size=3):
        """فیلتر میانه برای حذف نویز نقطه‌ای"""
        pad = kernel_size // 2
        padded = np.pad(arr, pad, mode='edge')
        out = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                out[i, j] = np.median(padded[i:i+kernel_size, j:j+kernel_size])
        return out

    @staticmethod
    def _sobel_magnitude(img):
        """محاسبه اندازه لبه با عملگر Sobel (پیاده‌سازی دستی، بدون scipy)"""
        sobel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]], dtype=np.float32)
        sobel_y = np.array([[-1, -2, -1],
                            [0, 0, 0],
                            [1, 2, 1]], dtype=np.float32)
        pad = 1
        padded = np.pad(img, pad, mode='edge')
        h, w = img.shape
        mag = np.zeros_like(img)
        for i in range(1, h+1):
            for j in range(1, w+1):
                window = padded[i-1:i+2, j-1:j+2]
                gx = np.sum(window * sobel_x)
                gy = np.sum(window * sobel_y)
                mag[i-1, j-1] = np.hypot(gx, gy)
        max_val = mag.max()
        if max_val > 0:
            mag /= max_val
        return mag

    def image_to_3d(self, image_path, output_obj="public/models/3d_object.obj",
                    max_res=300, max_height=0.28,
                    median_kernel=3, bg_threshold=0.85,
                    edge_boost=0.3, gamma=1.2):
        """
        تبدیل تصویر به مدل سه‌بعدی صفحه‌ای (Height Map) – نسخه پایدار و بدون scipy
        """
        # 1. بارگذاری و تبدیل به luminance
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        rgb = np.array(img, dtype=np.float32) / 255.0
        luminance = 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]
        h, w = luminance.shape

        # 2. فیلتر میانه
        if median_kernel > 1:
            luminance = self._median_filter(luminance, kernel_size=median_kernel)

        # 3. حذف زمینه روشن
        luminance[luminance > bg_threshold] = 1.0

        # 4. اعمال گاما و معکوس (تیره = ارتفاع بیشتر)
        if gamma != 1.0:
            luminance = np.power(luminance, gamma)
        depth = 1.0 - luminance

        # 5. تقویت لبه‌ها با Sobel
        if edge_boost > 0:
            edges = self._sobel_magnitude(luminance)
            depth = depth + edges * edge_boost
            depth = np.clip(depth, 0, 1)

        # 6. مقیاس نهایی ارتفاع
        depth = depth * max_height

        # 7. ساخت رئوس
        x_vals = np.linspace(0, 1, w, dtype=np.float32)
        y_vals = np.linspace(0, 1, h, dtype=np.float32)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = depth
        vertices = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
        vertices_list = vertices.tolist()

        # 8. مثلث‌بندی
        def idx(x, y):
            return y * w + x

        faces = []
        for y in range(h-1):
            for x in range(w-1):
                tl = idx(x, y)
                tr = idx(x+1, y)
                bl = idx(x, y+1)
                br = idx(x+1, y+1)

                a = np.array(vertices_list[tl])
                b = np.array(vertices_list[tr])
                c = np.array(vertices_list[bl])
                d = np.array(vertices_list[br])

                diag1 = np.linalg.norm(a - d)
                diag2 = np.linalg.norm(b - c)
                if diag1 <= diag2:
                    tri1 = (tl, bl, tr)
                    tri2 = (tr, bl, br)
                else:
                    tri1 = (tl, tr, bl)
                    tri2 = (tr, br, bl)

                # تصحیح جهت نرمال
                def correct(tri):
                    u0, v0 = x, y
                    u1 = x+1 if tri[1] in (tr, br) else x
                    v1 = y+1 if tri[1] in (bl, br) else y
                    u2 = x+1 if tri[2] in (tr, br) else x
                    v2 = y+1 if tri[2] in (bl, br) else y
                    area_uv = (u1 - u0)*(v2 - v0) - (u2 - u0)*(v1 - v0)
                    return (tri[0], tri[2], tri[1]) if area_uv < 0 else tri

                faces.append(correct(tri1))
                faces.append(correct(tri2))

        # 9. ذخیره فایل OBJ
        os.makedirs(os.path.dirname(output_obj), exist_ok=True)
        with open(output_obj, "w", encoding="utf-8") as f:
            f.write("# 3D Model - No SciPy, Pure NumPy\n")
            f.write(f"# max_height={max_height}, edge_boost={edge_boost}, max_res={max_res}\n")
            f.write(f"# vertices={len(vertices_list)}, faces={len(faces)}\n")
            for v in vertices_list:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

        self.model_path = output_obj
        print(f"[OK] Model saved: {len(vertices_list)} vertices, {len(faces)} faces -> {output_obj}")
        return True, output_obj


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        engine = Engine3D()
        engine.image_to_3d(
            sys.argv[1],
            sys.argv[2] if len(sys.argv) > 2 else "output.obj",
            max_res=300,
            max_height=0.28,
            median_kernel=3,
            bg_threshold=0.85,
            edge_boost=0.3,
            gamma=1.2
        )
    else:
        print("Usage: python engine_3d.py <image_path> [output.obj]")
