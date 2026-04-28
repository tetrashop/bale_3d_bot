import os
import sys
import math
import numpy as np
from PIL import Image

class Engine3D:
    def process(self, image_path, output_path="public/models/3d_object.obj", max_res=400):
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        width, height = img.size
        rgb = np.array(img, dtype=np.float32) / 255.0
        intensity = (rgb[:,:,0] + rgb[:,:,1] + rgb[:,:,2]) / 3.0

        max_height = 0.28
        vertices = []
        for y in range(height):
            for x in range(width):
                Z = intensity[y, x] * max_height
                X = (x / width) * 2 - 1
                Y = (y / height) * 2 - 1
                vertices.append((X, Y, Z))

        if len(vertices) < 3:
            return False, None

        vertices = np.array(vertices)
        center = vertices.mean(axis=0)
        vertices = vertices - center
        vertices = vertices.tolist()

        w = int(math.sqrt(len(vertices)))
        h = len(vertices) // w
        if w < 2 or h < 2:
            return False, None

        def idx(x, y):
            return y * w + x

        faces = []
        for y in range(h-1):
            for x in range(w-1):
                tl = idx(x, y)
                tr = idx(x+1, y)
                bl = idx(x, y+1)
                br = idx(x+1, y+1)
                a = vertices[tl]; b = vertices[tr]; c = vertices[bl]; d = vertices[br]
                diag1 = ((a[0]-d[0])**2 + (a[1]-d[1])**2 + (a[2]-d[2])**2)**0.5
                diag2 = ((b[0]-c[0])**2 + (b[1]-c[1])**2 + (b[2]-c[2])**2)**0.5
                if diag1 <= diag2:
                    faces.append((tl, bl, tr))
                    faces.append((tr, bl, br))
                else:
                    faces.append((tl, tr, bl))
                    faces.append((tr, br, bl))

        def correct_normal(tri):
            a = vertices[tri[0]]
            b = vertices[tri[1]]
            c = vertices[tri[2]]
            area_xy = (b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])
            if area_xy < 0:
                return (tri[0], tri[2], tri[1])
            return tri
        faces = [correct_normal(f) for f in faces]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 3D Model - Relief Sculpture (Final)\n")
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
