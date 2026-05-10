import os
import sys
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self, max_height=0.28, max_faces=4000):
        self.max_height = max_height
        self.max_faces = max_faces

    @staticmethod
    def median_filter_2d(arr, k=3):
        pad = k // 2
        h, w = arr.shape
        padded = np.pad(arr, pad, mode='edge')
        out = np.zeros_like(arr)
        for i in range(h):
            for j in range(w):
                out[i, j] = np.median(padded[i:i+k, j:j+k])
        return out

    def extract_intensity(self, image):
        rgb = np.array(image, dtype=np.float32) / 255.0
        intensity = (rgb[:,:,0] + rgb[:,:,1] + rgb[:,:,2]) / 3.0
        intensity = self.median_filter_2d(intensity, k=3)
        return intensity

    def intensity_to_vertices(self, intensity, max_res=150, stride=2):
        h, w = intensity.shape
        if max_res and max(w, h) > max_res:
            scale = max_res / max(w, h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img_pil = Image.fromarray((intensity * 255).astype(np.uint8))
            img_pil = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
            intensity = np.array(img_pil, dtype=np.float32) / 255.0
            h, w = new_h, new_w
        vertices = []
        for y in range(0, h, stride):
            for x in range(0, w, stride):
                X = (x / w) * 2.0 - 1.0
                Y = (y / h) * 2.0 - 1.0
                Z = intensity[y, x] * self.max_height
                vertices.append([X, Y, Z])
        return vertices, (h+stride-1)//stride, (w+stride-1)//stride

    def triangulate_grid(self, vertices, w, h):
        if w < 2 or h < 2:
            return []
        def idx(x, y):
            return y * w + x
        faces = []
        for y in range(h-1):
            for x in range(w-1):
                tl = idx(x, y)
                tr = idx(x+1, y)
                bl = idx(x, y+1)
                br = idx(x+1, y+1)
                a,b,c,d = vertices[tl], vertices[tr], vertices[bl], vertices[br]
                diag1 = (a[0]-d[0])**2 + (a[1]-d[1])**2 + (a[2]-d[2])**2
                diag2 = (b[0]-c[0])**2 + (b[1]-c[1])**2 + (b[2]-c[2])**2
                if diag1 <= diag2:
                    faces.append((tl, bl, tr)); faces.append((tr, bl, br))
                else:
                    faces.append((tl, tr, bl)); faces.append((tr, br, bl))
        return faces

    @staticmethod
    def fix_normals(vertices, faces):
        corrected = []
        for tri in faces:
            a,b,c = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
            area_xy = (b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])
            if area_xy < 0:
                corrected.append((tri[0], tri[2], tri[1]))
            else:
                corrected.append(tri)
        return corrected

    @staticmethod
    def center_and_scale(vertices):
        vertices = np.array(vertices, dtype=np.float32)
        center = vertices.mean(axis=0)
        vertices = vertices - center
        max_xy = max(vertices[:,0].max(), vertices[:,1].max())
        if max_xy > 0:
            vertices[:,0] /= max_xy
            vertices[:,1] /= max_xy
        max_z = vertices[:,2].max() if vertices[:,2].max() != 0 else 1.0
        vertices[:,2] = vertices[:,2] / max_z * 1.5
        return vertices.tolist()

    @staticmethod
    def save_obj(vertices, faces, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(f"# Engine3D\n# Vertices: {len(vertices)}, Faces: {len(faces)}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        return True

    def process(self, image_path, output_path="public/models/3d_object.obj", max_res=150):
        img = Image.open(image_path).convert('RGB')
        intensity = self.extract_intensity(img)
        vertices, w, h = self.intensity_to_vertices(intensity, max_res, stride=2)
        if len(vertices) < 4:
            return False, None
        faces = self.triangulate_grid(vertices, w, h)
        faces = self.fix_normals(vertices, faces)
        vertices = self.center_and_scale(vertices)

        if len(faces) > self.max_faces and self.max_faces > 0:
            step = max(2, len(faces) // self.max_faces)
            faces = faces[::step][:self.max_faces]

        self.save_obj(vertices, faces, output_path)
        return True, output_path
