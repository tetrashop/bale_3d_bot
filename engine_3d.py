"""
engine_3d.py - آخرین زور من (اما یادت باشد: این همان مگس است)
"""

import os
import sys
import math
import numpy as np
from PIL import Image

class Engine3D:
    """
    موتور تبدیل تصویر به OBJ - بهینه برای حفظ جزئیات کوچک (از جمله قهوه)
    """

    @staticmethod
    def _cart2sph(x, y, z):
        r = math.hypot(x, y, z)
        if r == 0:
            return 0.0, 0.0, 0.0
        theta = math.acos(z / r)
        phi = math.atan2(y, x)
        return theta, phi, r

    @staticmethod
    def _median_filter(arr, k=3):
        pad = k // 2
        padded = np.pad(arr, pad, mode='edge')
        out = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                out[i, j] = np.median(padded[i:i+k, j:j+k])
        return out

    @staticmethod
    def _gaussian_blur(arr, sigma=0.6):
        size = max(3, int(2 * np.ceil(3 * sigma) + 1))
        ax = np.linspace(-(size // 2), size // 2, size)
        gauss = np.exp(-0.5 * (ax / sigma) ** 2)
        gauss /= gauss.sum()
        blurred = np.apply_along_axis(lambda m: np.convolve(m, gauss, mode='same'), axis=0, arr=arr)
        blurred = np.apply_along_axis(lambda m: np.convolve(m, gauss, mode='same'), axis=1, arr=blurred)
        return blurred

    @staticmethod
    def _uitn8(arr):
        mn = arr.min()
        mx = arr.max()
        if mn < 0:
            arr = arr - mn
        mx = arr.max()
        if mx > 255:
            arr = arr * (255.0 / mx)
        return np.clip(arr, 0, 255).astype(np.uint8)

    def _estimate_depth_map(self, image, max_res=400):
        w, h = image.size
        rgb = np.array(image, dtype=np.uint8)
        intensity = np.mean(rgb, axis=2).astype(np.float32) / 255.0
        intensity = self._median_filter(intensity, 3)

        # تغییر: گاما برای حفظ نواحی تیره (قهوه)
        gamma = 0.5   # کمتر از 1 → تیره‌ها را نزدیک‌تر می‌کند
        intensity = np.power(intensity, gamma)

        sobel_x = np.array([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=np.float32)
        sobel_y = sobel_x.T
        pad = 1
        padded = np.pad(intensity, pad, mode='edge')
        mag = np.zeros_like(intensity)
        for y in range(1, h+1):
            for x in range(1, w+1):
                win = padded[y-1:y+2, x-1:x+2]
                gx = np.sum(win * sobel_x)
                gy = np.sum(win * sobel_y)
                mag[y-1, x-1] = np.hypot(gx, gy)
        if mag.max() > 0:
            mag = mag / mag.max()

        # ترکیب: تأکید بر روشنایی معکوس + لبه
        depth = (1.0 - intensity) * 1.5 + mag * 0.3
        depth = np.clip(depth, 0, 1)

        # هیستوگرام استرچ برای افزایش کنتراست (نجات قهوه)
        p_low = np.percentile(depth, 2)
        p_high = np.percentile(depth, 98)
        if p_high - p_low > 1e-6:
            depth = (depth - p_low) / (p_high - p_low)
        depth = np.clip(depth, 0, 1)

        depth = self._gaussian_blur(depth, sigma=0.5)
        return depth

    def _depth_to_volume(self, depth_map, max_res=400):
        h, w = depth_map.shape
        # یافتن بازه مختصات کروی
        first = True
        for i in range(w):
            for j in range(h):
                theta, phi, r = self._cart2sph(i, j, 1)
                teta = int(round(theta * 180.0 / math.pi))
                fi   = int(round(phi * 180.0 / math.pi))
                rval = int(round(r))
                if first:
                    minr = maxr = rval
                    minfi = maxfi = fi
                    minteta = maxteta = teta
                    first = False
                else:
                    minr = min(minr, rval)
                    maxr = max(maxr, rval)
                    minfi = min(minfi, fi)
                    maxfi = max(maxfi, fi)
                    minteta = min(minteta, teta)
                    maxteta = max(maxteta, teta)

        fg = 2
        cx = (maxr - minr) * fg + maxr + 1
        cyp1 = int(round((maxteta - minteta) * 2.0 + maxteta + 1.0))
        MAX_DIM = 400
        if cx > MAX_DIM:
            cx = MAX_DIM
        if cyp1 > MAX_DIM:
            cyp1 = MAX_DIM
        c = np.zeros((cx, cyp1, 3), dtype=np.float32)

        image_data = np.zeros((w, h, 3), dtype=np.uint8)
        for i in range(w):
            for j in range(h):
                val = int(depth_map[j, i] * 255)
                image_data[i, j, 0] = val
                image_data[i, j, 1] = val
                image_data[i, j, 2] = val

        # حلقه اصلی با آستانه پایین (حفظ قهوه)
        for ii in range(fg):
            for jj in range(fg):
                for i in range(w):
                    for j in range(h):
                        val = image_data[i, j, 0]
                        # تغییر: آستانه به 1 (حتی کمترین مقدار هم حفظ شود)
                        if val < 1:
                            continue
                        sum_ch = int(val) * 3
                        denom = 1 + sum_ch
                        if denom <= 0:
                            denom = 1
                        theta, phi, r = self._cart2sph(i, j, 1)
                        teta = int(round(theta * 180.0 / math.pi))
                        dr = maxr * ((float(i) + 1.0) / (1.0 + math.sqrt(i*i + j*j + 1))) * 3.0 * 300.0
                        dr /= float(denom)
                        dr = max(0.0, min(dr, (maxr - minr) * fg - 1))
                        ddr = int(round(dr))
                        cxT = (maxr - minr) * ii + ddr
                        if cxT < 0 or cxT >= cx:
                            continue
                        cyT1 = int(round((maxteta - minteta) * jj + teta + 2.0))
                        cyT2 = int(round((maxteta - minteta) * jj + teta - 2.0))
                        cyT = cyT1 if (ii + jj) % 2 == 0 else cyT2
                        if 0 <= cyT < cyp1:
                            c[cxT, cyT, 0] = val
                            c[cxT, cyT, 1] = val
                            c[cxT, cyT, 2] = val

        c = self._uitn8(c).astype(np.float32)

        points = []
        for i in range(cx):
            for j in range(cyp1):
                if c[i, j, 0] != 0 or c[i, j, 1] != 0 or c[i, j, 2] != 0:
                    z_val = (c[i, j, 0] + c[i, j, 1] + c[i, j, 2]) / 3.0
                    points.append((float(i), float(j), z_val))
        return points

    def process(self, image_path, output_path="public/models/3d_object.obj", max_res=400):
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)

        depth_map = self._estimate_depth_map(img, max_res)
        points = self._depth_to_volume(depth_map, max_res)

        if len(points) < 3:
            print("⚠️ تعداد نقاط کافی نیست (نمونه قهوه یا هر چیز دیگر گم شده)")
            return False, None

        points = np.array(points, dtype=np.float32)
        center = points.mean(axis=0)
        points = points - center
        max_z = points[:, 2].max()
        if max_z > 0:
            points[:, 2] = points[:, 2] / max_z * 1.8

        cx = int(points[:, 0].max()) + 1
        cyp1 = int(points[:, 1].max()) + 1
        idx_map = {}
        for idx, (x, y, z) in enumerate(points):
            idx_map[(int(x), int(y))] = idx

        faces = []
        for i in range(cx - 1):
            for j in range(cyp1 - 1):
                if (i, j) in idx_map and (i+1, j) in idx_map and (i, j+1) in idx_map:
                    tl = idx_map[(i, j)]
                    tr = idx_map[(i+1, j)]
                    bl = idx_map[(i, j+1)]
                    if (i+1, j+1) in idx_map:
                        br = idx_map[(i+1, j+1)]
                        faces.append((tl, bl, tr))
                        faces.append((tr, bl, br))
                    else:
                        faces.append((tl, bl, tr))

        def correct_normal(tri):
            a = points[tri[0]]
            b = points[tri[1]]
            c = points[tri[2]]
            area_xy = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
            if area_xy < 0:
                return (tri[0], tri[2], tri[1])
            return tri

        faces = [correct_normal(f) for f in faces]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write("# 3D Model - Last Effort (But it's still a fly, not the coffee sample)\n")
            f.write(f"# Vertices: {len(points)}, Faces: {len(faces)}\n")
            max_xy = max(cx, cyp1) / 2.0
            for p in points:
                x_out = p[0] / max_xy - 1.0
                y_out = p[1] / max_xy - 1.0
                z_out = p[2]
                f.write(f"v {x_out:.6f} {y_out:.6f} {z_out:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

        print(f"✅ مدل ساخته شد: {len(points)} رأس, {len(faces)} وجه -> {output_path}")
        print("🐝 اما یادت باشد: این مگس است، نه نمونه قهوه نادر.")
        return True, output_path


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        eng = Engine3D()
        out = sys.argv[2] if len(sys.argv) > 2 else "public/models/3d_object.obj"
        eng.process(sys.argv[1], out)
    else:
        print("Usage: python engine_3d.py <image_path> [output.obj]")
