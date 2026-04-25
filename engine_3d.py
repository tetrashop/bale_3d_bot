import os
import sys
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None

    def image_to_3d_spherical(self, image_path, output_obj="public/models/3d_object.obj", max_res=300):
        """
        تبدیل هر نوع تصویر (رنگی یا خاکستری) به مدل OBJ با توپوگرافی کروی.
        در صورت رنگی بودن، ابتدا به灰度 تبدیل می‌شود.
        """
        img = Image.open(image_path)
        # اطمینان از灰度 بودن
        if img.mode != 'L':
            img = img.convert('L')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        image = np.array(img)   # آرایه 2 بعدی خاکستری

        h, w = image.shape
        cx, cy = w / 2, h / 2
        max_r = np.sqrt(cx**2 + cy**2)

        vertices = []
        for y in range(h):
            for x in range(w):
                dx = x - cx
                dy = y - cy
                theta = (dx / max_r) * np.pi
                phi = (dy / max_r) * (np.pi / 2)
                intensity = image[y, x] / 255.0
                r = intensity
                X = r * np.sin(phi) * np.cos(theta)
                Y = r * np.sin(phi) * np.sin(theta)
                Z = r * np.cos(phi)
                vertices.append((X, Y, Z))

        def vid(x_, y_):
            return y_ * w + x_ + 1

        def is_valid_triangle(v1, v2, v3, axis=np.array([0,0,1]), angle_threshold_deg=10):
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
            return not (angle_deg < angle_threshold_deg or angle_deg > (180 - angle_threshold_deg))

        faces = []
        for y in range(h - 1):
            for x in range(w - 1):
                v1 = vid(x, y)
                v2 = vid(x + 1, y)
                v3 = vid(x, y + 1)
                v4 = vid(x + 1, y + 1)

                if is_valid_triangle(vertices[v1-1], vertices[v2-1], vertices[v3-1]):
                    faces.append((v1, v2, v3))
                if is_valid_triangle(vertices[v3-1], vertices[v2-1], vertices[v4-1]):
                    faces.append((v3, v2, v4))

        os.makedirs(os.path.dirname(output_obj), exist_ok=True)
        with open(output_obj, "w") as f:
            f.write("# OBJ model from 2D image (grayscale converted)\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")

        self.model_path = output_obj
        print(f"مدل سه‌بعدی در {output_obj} ذخیره شد.")
        return True, output_obj

    # سایر متدهای کلاس (در صورت نیاز) می‌توانند بدون تغییر اضافه شوند.
