#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine_3d.py - موتور تبدیل تصویر 2D به مدل سه‌بعدی OBJ
نسخه نهایی با بالاترین بهره‌وری و کیفیت
"""

import os
import sys
import math
import numpy as np
from PIL import Image

class Engine3D:
    """موتور تبدیل تصویر 2D به مدل سه‌بعدی OBJ"""
    
    def __init__(self):
        self.model_path = None
        self.vertices = []
        self.faces = []
    
    @staticmethod
    def _get_luminance(rgb):
        """محاسبه روشنایی (Luminance) از تصویر RGB"""
        return 0.299 * rgb[:,:,0] + 0.587 * rgb[:,:,1] + 0.114 * rgb[:,:,2]
    
    @staticmethod
    def _median_filter(arr, kernel=3):
        """فیلتر میانه برای حذف نویز نقطه‌ای"""
        pad = kernel // 2
        padded = np.pad(arr, pad, mode='edge')
        out = np.zeros_like(arr)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                out[i, j] = np.median(padded[i:i+kernel, j:j+kernel])
        return out
    
    @staticmethod
    def _gaussian_blur(arr, sigma=0.8):
        """فیلتر گوسین برای هموارسازی"""
        size = int(2 * np.ceil(3 * sigma) + 1)
        if size < 3:
            size = 3
        ax = np.linspace(-(size // 2), size // 2, size)
        gauss = np.exp(-0.5 * (ax / sigma) ** 2)
        gauss /= gauss.sum()
        blurred = np.apply_along_axis(lambda m: np.convolve(m, gauss, mode='same'), axis=0, arr=arr)
        blurred = np.apply_along_axis(lambda m: np.convolve(m, gauss, mode='same'), axis=1, arr=blurred)
        return blurred
    
    @staticmethod
    def _sobel_edges(img):
        """لبه‌یاب Sobel برای استخراج لبه‌ها"""
        sobel_x = np.array([[-1,0,1], [-2,0,2], [-1,0,1]], dtype=np.float32)
        sobel_y = sobel_x.T
        pad = 1
        padded = np.pad(img, pad, mode='edge')
        h, w = img.shape
        mag = np.zeros_like(img)
        for y in range(1, h+1):
            for x in range(1, w+1):
                window = padded[y-1:y+2, x-1:x+2]
                gx = np.sum(window * sobel_x)
                gy = np.sum(window * sobel_y)
                mag[y-1, x-1] = np.hypot(gx, gy)
        max_val = mag.max()
        return mag / max_val if max_val > 0 else mag
    
    def process(self, image_path, output_path="public/models/3d_object.obj", 
                max_res=400, quality="high", edge_boost=0.3, smooth_sigma=0.6):
        """
        پردازش اصلی تبدیل تصویر به مدل سه‌بعدی
        
        پارامترها:
            image_path: مسیر تصویر ورودی
            output_path: مسیر خروجی OBJ
            max_res: حداکثر ابعاد تصویر
            quality: "low", "medium", "high"
            edge_boost: میزان تقویت لبه‌ها (0 تا 0.5)
            smooth_sigma: میزان هموارسازی (0.3 تا 1.0)
        """
        # تنظیمات کیفیت
        quality_settings = {
            'low': {'max_res': 200, 'threshold': 0.85, 'max_height': 0.25},
            'medium': {'max_res': 300, 'threshold': 0.85, 'max_height': 0.28},
            'high': {'max_res': 400, 'threshold': 0.85, 'max_height': 0.30}
        }
        settings = quality_settings.get(quality, quality_settings['high'])
        if max_res < settings['max_res']:
            settings['max_res'] = max_res
        
        # 1. بارگذاری تصویر
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((settings['max_res'], settings['max_res']), Image.Resampling.LANCZOS)
        width, height = img.size
        rgb = np.array(img, dtype=np.float32) / 255.0
        
        # 2. محاسبه روشنایی و پیش‌پردازش
        luminance = self._get_luminance(rgb)
        luminance = self._median_filter(luminance, kernel=3)
        luminance[luminance > settings['threshold']] = 1.0
        
        # 3. اعمال گاما و معکوس
        gamma = 1.2
        luminance = np.power(luminance, gamma)
        depth = 1.0 - luminance  # تیره = بلند
        
        # 4. تقویت لبه (اختیاری)
        if edge_boost > 0:
            edges = self._sobel_edges(luminance)
            depth = depth + edges * edge_boost
            depth = np.clip(depth, 0, 1)
        
        # 5. هموارسازی
        if smooth_sigma > 0:
            depth = self._gaussian_blur(depth, sigma=smooth_sigma)
        
        # 6. مقیاس ارتفاع نهایی
        depth = depth * settings['max_height']
        
        # 7. ساخت رئوس (مختصات کروی ساده شده)
        vertices = []
        for y in range(height):
            for x in range(width):
                r = depth[y, x]
                angle = (y / height) * math.pi
                
                X = (x / width) * 2 - 1
                Y = (y / height) * 2 - 1
                Z = r * math.sin(angle) * 0.5
                
                vertices.append((X, Y, Z))
        
        # 8. مثلث‌بندی بهینه
        w = int(math.sqrt(len(vertices)))
        h = len(vertices) // w
        
        def idx(x, y):
            return y * w + x
        
        faces = []
        for y in range(h - 1):
            for x in range(w - 1):
                tl = idx(x, y)
                tr = idx(x + 1, y)
                bl = idx(x, y + 1)
                br = idx(x + 1, y + 1)
                
                # انتخاب قطر کوتاه‌تر
                a = vertices[tl]
                b = vertices[tr]
                c = vertices[bl]
                d = vertices[br]
                
                diag1 = ((a[0]-d[0])**2 + (a[1]-d[1])**2 + (a[2]-d[2])**2)**0.5
                diag2 = ((b[0]-c[0])**2 + (b[1]-c[1])**2 + (b[2]-c[2])**2)**0.5
                
                if diag1 <= diag2:
                    faces.append((tl, bl, tr))
                    faces.append((tr, bl, br))
                else:
                    faces.append((tl, tr, bl))
                    faces.append((tr, br, bl))
        
        # 9. ذخیره فایل OBJ
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 3D Model - Optimized Engine\n")
            f.write(f"# Quality: {quality}, Vertices: {len(vertices)}, Faces: {len(faces)}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        
        print(f"[OK] Model saved: {len(vertices)} vertices, {len(faces)} faces -> {output_path}")
        return True, output_path


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        engine = Engine3D()
        engine.process(
            sys.argv[1],
            sys.argv[2] if len(sys.argv) > 2 else "output.obj",
            max_res=400,
            quality="high"
        )
    else:
        print("Usage: python engine_3d.py <image_path> [output.obj]")
