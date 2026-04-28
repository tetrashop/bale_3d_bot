import os
import sys
import math
import numpy as np
from PIL import Image
from collections import defaultdict
from scipy.interpolate import griddata

class Engine3D:
    def process(self, image_path, output_path="public/models/3d_object.obj", 
                max_res=400, target_vertices=15000, remove_outliers=True):
        # ========== 1. بارگذاری و شدت روشنایی ==========
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        width, height = img.size
        rgb = np.array(img, dtype=np.float32) / 255.0
        intensity = (rgb[:,:,0] + rgb[:,:,1] + rgb[:,:,2]) / 3.0

        # فیلتر میانه (اختیاری، نویز را کاهش می‌دهد)
        from scipy.ndimage import median_filter
        intensity = median_filter(intensity, size=3)

        # ========== 2. ساخت رئوس با فرمول اصلی (بدون تغییر مقادیر) ==========
        vertices = []
        for y in range(height):
            for x in range(width):
                r = intensity[y, x]
                angle = (x / width) * 2 * math.pi
                # فرمول اصلی – بدون هیچ ضریب اضافی
                Z = r * math.cos(angle)      # دامنه عمق [-1, 1]
                X = (x / width) * 2 - 1
                Y = (y / height) * 2 - 1
                vertices.append((X, Y, Z))

        if len(vertices) < 3:
            return False, None

        # ========== 3. حذف رئوس پرت (اختیاری) ==========
        if remove_outliers:
            vertices = np.array(vertices)
            z_vals = vertices[:, 2]
            mean_z = np.mean(z_vals)
            std_z = np.std(z_vals)
            lower_bound = mean_z - 3 * std_z
            upper_bound = mean_z + 3 * std_z
            mask = (z_vals >= lower_bound) & (z_vals <= upper_bound)
            vertices = vertices[mask]
            vertices = vertices.tolist()

        # ========== 4. مرکزی‌سازی خودکار (قرارگیری کامل در کادر) ==========
        vertices = np.array(vertices)
        min_vals = vertices.min(axis=0)
        max_vals = vertices.max(axis=0)
        # انتقال به مرکز کادر (نه مرکز هندسی ساده)
        center = (min_vals + max_vals) / 2
        vertices = vertices - center
        # مقیاس‌بندی به [-1,1] برای دید بهتر
        max_range = np.max(max_vals - min_vals) / 2
        if max_range > 0:
            vertices = vertices / max_range
        vertices = vertices.tolist()

        # ========== 5. اگر رئوس کم است، درون‌یابی چندجمله‌ای ==========
        if len(vertices) < 1000:  # آستانه کمبود رئوس
            print("⚠️ تعداد رئوس کم است، درون‌یابی انجام می‌شود...")
            # ایجاد نقاط منظم جدید
            xs = np.linspace(-1, 1, max_res)
            ys = np.linspace(-1, 1, max_res)
            X, Y = np.meshgrid(xs, ys)
            points = np.array([(v[0], v[1]) for v in vertices])
            values = np.array([v[2] for v in vertices])
            # درون‌یابی با روش خطی
            Z_new = griddata(points, values, (X, Y), method='linear', fill_value=0)
            # ساخت رئوس جدید
            vertices = []
            for i in range(max_res):
                for j in range(max_res):
                    z_val = Z_new[i, j]
                    if not np.isnan(z_val):
                        vertices.append((xs[j], ys[i], z_val))

        # ========== 6. مثلث‌بندی Delaunay ==========
        try:
            from scipy.spatial import Delaunay
            points_2d = [(v[0], v[1]) for v in vertices]
            tri = Delaunay(points_2d)
            faces = tri.simplices.tolist()
        except ImportError:
            # Fallback: مثلث‌بندی شبکه منظم
            n = len(vertices)
            grid_size = int(math.sqrt(n))
            def idx(x, y):
                return y * grid_size + x
            faces = []
            for y in range(grid_size - 1):
                for x in range(grid_size - 1):
                    if idx(x, y) < n and idx(x+1, y+1) < n:
                        faces.append((idx(x, y), idx(x+1, y), idx(x, y+1)))
                        faces.append((idx(x+1, y+1), idx(x+1, y), idx(x, y+1)))

        # ========== 7. کاهش رئوس هوشمند (در صورت نیاز) ==========
        if len(faces) > target_vertices:
            from scipy.spatial import Delaunay
            # نمونه‌برداری منظم برای کاهش
            step = int(len(vertices) / target_vertices)
            indices = list(range(0, len(vertices), step))[:target_vertices]
            vertices = [vertices[i] for i in indices]
            points_2d = [(v[0], v[1]) for v in vertices]
            tri = Delaunay(points_2d)
            faces = tri.simplices.tolist()

        # ========== 8. تصحیح نرمال‌ها ==========
        def correct_normal(tri):
            a = vertices[tri[0]]
            b = vertices[tri[1]]
            c = vertices[tri[2]]
            area_xy = (b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])
            if area_xy < 0:
                return (tri[0], tri[2], tri[1])
            return tri
        faces = [correct_normal(f) for f in faces]

        # ========== 9. ذخیره OBJ ==========
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 3D Model - Final Improved Algorithm\n")
            f.write(f"# Vertices: {len(vertices)}, Faces: {len(faces)}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

        print(f"[OK] Model saved: {len(vertices)} vertices, {len(faces)} faces -> {output_path}")
        return True, output_path

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        eng = Engine3D()
        out = sys.argv[2] if len(sys.argv) > 2 else "public/models/3d_object.obj"
        eng.process(sys.argv[1], out)
    else:
        print("Usage: python engine_3d.py <image_path> [output.obj]")
