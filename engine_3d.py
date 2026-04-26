import os
import sys
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None

    def _median_filter(self, arr, kernel_size=3):
        """فیلتر میانه برای حذف نویزهای ضربه‌ای (میله‌ای) - بدون scipy"""
        pad = kernel_size // 2
        arr_pad = np.pad(arr, pad, mode='edge')
        result = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                window = arr_pad[i:i+kernel_size, j:j+kernel_size]
                result[i, j] = np.median(window)
        return result

    def _sobel_edges(self, img):
        """لبه‌یاب Sobel با numpy خالص"""
        h, w = img.shape
        sobel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]], dtype=np.float32)
        sobel_y = np.array([[-1, -2, -1],
                            [ 0,  0,  0],
                            [ 1,  2,  1]], dtype=np.float32)
        img_pad = np.pad(img, pad_width=1, mode='edge')
        mag = np.zeros_like(img)
        for y in range(1, h+1):
            for x in range(1, w+1):
                window = img_pad[y-1:y+2, x-1:x+2]
                gx = np.sum(window * sobel_x)
                gy = np.sum(window * sobel_y)
                mag[y-1, x-1] = np.hypot(gx, gy)
        max_val = mag.max()
        if max_val > 0:
            mag = mag / max_val
        return mag

    def image_to_3d(self, image_path, output_obj="public/models/3d_object.obj",
                    max_res=400, max_height=0.28,
                    edge_boost=0.4, edge_sigma=0.8,
                    gamma=1.2, invert=True,
                    bg_threshold=0.85, bg_flat=True,
                    median_filter_size=3):
        """
        تبدیل تصویر به مدل سه‌بعدی با فیلتر میانه برای حذف نویزهای میله‌ای
        """
        # 1. بارگذاری و لومینانس
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        rgb = np.array(img, dtype=np.float32) / 255.0
        luminance = 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]
        h, w = luminance.shape

        # 2. فیلتر میانه روی تصویر اصلی (کاهش نویز)
        if median_filter_size > 1:
            luminance = self._median_filter(luminance, kernel_size=median_filter_size)

        # 3. لبه‌ها
        edges = self._sobel_edges(luminance)

        # 4. گاما و معکوس
        if gamma != 1.0:
            lum_gamma = np.power(luminance, gamma)
        else:
            lum_gamma = luminance
        if invert:
            depth_base = 1.0 - lum_gamma
        else:
            depth_base = lum_gamma

        # 5. تخت کردن زمینه
        if bg_flat:
            depth_base[luminance > bg_threshold] = 0.0

        # 6. ترکیب با لبه‌ها
        edge_map = np.tanh(edges * edge_sigma) * edge_boost
        depth = depth_base + edge_map
        depth = np.clip(depth, 0, 1)

        # 7. فیلتر میانه روی نقشه ارتفاع (حذف نویزهای نهایی)
        if median_filter_size > 1:
            depth = self._median_filter(depth, kernel_size=median_filter_size)

        # 8. مقیاس نهایی
        depth = depth * max_height

        # 9. مختصات
        x_vals = np.linspace(0, 1, w, dtype=np.float32)
        y_vals = np.linspace(0, 1, h, dtype=np.float32)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = depth

        vertices = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
        vertices_list = vertices.tolist()

        # 10. مثلث‌بندی
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

                def correct(tri):
                    u0, v0 = x, y
                    if tri[1] == tr or tri[1] == br:
                        u1 = x+1
                    else:
                        u1 = x
                    if tri[1] == tl or tri[1] == tr:
                        v1 = y
                    else:
                        v1 = y+1
                    if tri[2] == tr or tri[2] == br:
                        u2 = x+1
                    else:
                        u2 = x
                    if tri[2] == tl or tri[2] == tr:
                        v2 = y
                    else:
                        v2 = y+1
                    area_uv = (u1 - u0)*(v2 - v0) - (u2 - u0)*(v1 - v0)
                    if area_uv < 0:
                        return (tri[0], tri[2], tri[1])
                    return tri

                faces.append(correct(tri1))
                faces.append(correct(tri2))

        # 11. ذخیره
        os.makedirs(os.path.dirname(output_obj), exist_ok=True)
        with open(output_obj, "w", encoding="utf-8") as f:
            f.write("# Denoised 3D model (median filter)\n")
            f.write(f"# max_height={max_height}, edge_boost={edge_boost}, median_filter={median_filter_size}\n")
            for v in vertices_list:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

        self.model_path = output_obj
        print(f"[OK] مدل بدون نویز در {output_obj} ذخیره شد.")
        return True, output_obj

    def image_to_height_map(self, *args, **kwargs):
        return self.image_to_3d(*args, **kwargs)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        engine = Engine3D()
        engine.image_to_3d(sys.argv[1],
                           sys.argv[2] if len(sys.argv) > 2 else "output.obj",
                           max_res=400,
                           max_height=0.28,
                           edge_boost=0.4,
                           edge_sigma=0.8,
                           gamma=1.2,
                           invert=True,
                           bg_threshold=0.85,
                           bg_flat=True,
                           median_filter_size=3)
    else:
        print("استفاده: python engine_3d.py <image_path> [output.obj]")
