import os
import sys
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None

    # ---------- فیلتر میانه (حذف نویز ضربه‌ای) ----------
    def _median_filter(self, arr, kernel_size=3):
        pad = kernel_size // 2
        arr_pad = np.pad(arr, pad, mode='edge')
        result = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                window = arr_pad[i:i+kernel_size, j:j+kernel_size]
                result[i, j] = np.median(window)
        return result

    # ---------- لبه‌یاب Sobel (دستی، برای استخراج لبه‌های بال و بدن) ----------
    def _sobel_edges(self, img):
        h, w = img.shape
        sobel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]], dtype=np.float32)
        sobel_y = np.array([[-1, -2, -1],
                            [ 0,  0,  0],
                            [ 1,  2,  1]], dtype=np.float32)
        img_pad = np.pad(img, 1, mode='edge')
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

    # ---------- بستن منحنی‌ها با حاشیه صفر (جدا کردن کامل مگس از زمینه) ----------
    def _close_boundary(self, depth, margin=2, decay=0.7):
        h, w = depth.shape
        new_h, new_w = h + 2*margin, w + 2*margin
        new_depth = np.zeros((new_h, new_w), dtype=depth.dtype)
        new_depth[margin:margin+h, margin:margin+w] = depth
        
        # درون‌یابی حاشیه به سمت صفر (با ضریب کاهش)
        for i in range(margin):
            factor = decay ** (i+1)
            # بالا و پایین
            new_depth[i, margin:margin+w] = depth[0, :] * factor
            new_depth[new_h-1-i, margin:margin+w] = depth[-1, :] * factor
            # چپ و راست
            new_depth[margin:margin+h, i] = depth[:, 0] * factor
            new_depth[margin:margin+h, new_w-1-i] = depth[:, -1] * factor
        # گوشه‌ها (میانگین دو لبه)
        for i in range(margin):
            for j in range(margin):
                new_depth[i, j] = (new_depth[i, margin] + new_depth[margin, j]) / 2
                new_depth[i, new_w-1-j] = (new_depth[i, new_w-1-margin] + new_depth[margin, new_w-1-j]) / 2
                new_depth[new_h-1-i, j] = (new_depth[new_h-1-i, margin] + new_depth[new_h-1-margin, j]) / 2
                new_depth[new_h-1-i, new_w-1-j] = (new_depth[new_h-1-i, new_w-1-margin] + new_depth[new_h-1-margin, new_w-1-j]) / 2
        return new_depth

    # ---------- تبدیل اصلی ----------
    def image_to_3d(self, image_path, output_obj="public/models/3d_object.obj",
                    max_res=500, max_height=0.32,
                    edge_boost=0.5, edge_sigma=1.2,
                    gamma=1.2, invert=True,
                    bg_threshold=0.75, bg_flat=True,
                    median_filter_size=3,
                    boundary_margin=2, boundary_decay=0.6):
        """
        تبدیل تصویر به مدل سه‌بعدی با کیفیت بالا (فقط numpy و PIL)
        """
        # 1. بارگذاری و تبدیل به لومینانس (0..255)
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        rgb = np.array(img, dtype=np.float32) / 255.0
        luminance = 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]
        h, w = luminance.shape

        # 2. فیلتر میانه روی لومینانس (کاهش نویز تصویر)
        if median_filter_size > 1:
            luminance = self._median_filter(luminance, kernel_size=median_filter_size)

        # 3. لبه‌ها (Sobel)
        edges = self._sobel_edges(luminance)

        # 4. گاما و معکوس (تیره = بلند)
        if gamma != 1.0:
            lum_gamma = np.power(luminance, gamma)
        else:
            lum_gamma = luminance
        if invert:
            depth_base = 1.0 - lum_gamma
        else:
            depth_base = lum_gamma

        # 5. تخت کردن زمینه (حذف پیکسل‌های روشن)
        if bg_flat:
            depth_base[luminance > bg_threshold] = 0.0

        # 6. ترکیب با لبه‌ها (افزایش جزئیات)
        edge_map = np.tanh(edges * edge_sigma) * edge_boost
        depth = depth_base + edge_map
        depth = np.clip(depth, 0, 1)

        # 7. فیلتر میانه روی نقشه ارتفاع (حذف نویزهای باقی‌مانده)
        if median_filter_size > 1:
            depth = self._median_filter(depth, kernel_size=2)   # kernel کوچکتر برای حفظ جزئیات

        # 8. بستن منحنی‌ها (حاشیه صفر برای جداسازی قطعی مگس از زمینه)
        if boundary_margin > 0:
            depth = self._close_boundary(depth, margin=boundary_margin, decay=boundary_decay)

        # 9. مقیاس نهایی ارتفاع
        depth = depth * max_height
        h, w = depth.shape   # ابعاد پس از بستن مرز

        # 10. مختصات x,y در بازه [0,1] (بدون -1 و 1 برای جلوگیری از اعوجاج)
        x_vals = np.linspace(0, 1, w, dtype=np.float32)
        y_vals = np.linspace(0, 1, h, dtype=np.float32)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = depth

        vertices = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
        vertices_list = vertices.tolist()

        # 11. مثلث‌بندی با انتخاب کوتاه‌ترین قطر و تصحیح نرمال
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

        # 12. ذخیره فایل OBJ
        os.makedirs(os.path.dirname(output_obj), exist_ok=True)
        with open(output_obj, "w", encoding="utf-8") as f:
            f.write("# 3D Mosquito Model (no scipy, no opencv)\n")
            f.write(f"# max_height={max_height}, edge_boost={edge_boost}\n")
            f.write(f"# boundary_margin={boundary_margin}, boundary_decay={boundary_decay}\n")
            for v in vertices_list:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

        self.model_path = output_obj
        print(f"[OK] مدل نهایی مگس با جداسازی کامل زمینه در {output_obj} ذخیره شد. (رئوس: {len(vertices_list)}, وجه‌ها: {len(faces)})")
        return True, output_obj

    # سازگاری با نام‌های قبلی
    def image_to_height_map(self, *args, **kwargs):
        return self.image_to_3d(*args, **kwargs)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        engine = Engine3D()
        engine.image_to_3d(
            sys.argv[1],
            sys.argv[2] if len(sys.argv) > 2 else "output.obj",
            max_res=500,
            max_height=0.32,
            edge_boost=0.5,
            edge_sigma=1.2,
            gamma=1.2,
            invert=True,
            bg_threshold=0.75,
            bg_flat=True,
            median_filter_size=3,
            boundary_margin=2,
            boundary_decay=0.6
        )
    else:
        print("استفاده: python engine_3d.py <image_path> [output.obj]")
