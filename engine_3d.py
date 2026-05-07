import os
import sys
import numpy as np
from PIL import Image

class Engine3d:
    @staticmethod
    def _create_height_mesh(image_path, max_res, z_scale):
        img = Image.open(image_path).convert('L')
        img.thumbnail((max_res, max_res), Image.Resampling.LANCZOS)
        width, height = img.size
        img_array = np.array(img, dtype=np.float32)
        min_val = img_array.min()
        max_val = img_array.max()
        if max_val - min_val < 1e-6:
            z_vals = np.zeros_like(img_array)
        else:
            z_vals = (img_array - min_val) / (max_val - min_val) * z_scale
        z_vals = np.nan_to_num(z_vals, nan=0.0)
        x_coords = np.linspace(-1, 1, width)
        y_coords = np.linspace(-1, 1, height)
        xv, yv = np.meshgrid(x_coords, y_coords)
        vertices = np.stack([xv, yv, z_vals], axis=-1).reshape(-1, 3)
        # ساخت faces
        faces = []
        for i in range(height - 1):
            for j in range(width - 1):
                idx = i * width + j
                idx_r = idx + 1
                idx_b = idx + width
                idx_br = idx_b + 1
                if idx_br < len(vertices):
                    faces.append([idx, idx_r, idx_b])
                    faces.append([idx_r, idx_br, idx_b])
        return vertices, np.array(faces) if faces else np.empty((0,3))

    def process(self, image_path, output_path, max_res=300, z_scale=0.5):
        vertices, faces = self._create_height_mesh(image_path, max_res, z_scale)
        if len(vertices) == 0:
            return False, None
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Height map mesh\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        return True, output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python engine_3d.py <image_path> [output.obj] [max_res] [z_scale]")
        sys.exit(1)
    img_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "public/models/3d_object.obj"
    max_res = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    z_scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    eng = Engine3d()
    eng.process(img_path, out_path, max_res, z_scale)
