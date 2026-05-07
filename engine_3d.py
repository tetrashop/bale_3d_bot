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
        min_val, max_val = img_array.min(), img_array.max()
        if max_val - min_val < 1e-8:
            z_vals = np.zeros_like(img_array)
        else:
            z_vals = (img_array - min_val) / (max_val - min_val) * z_scale
        x_coords = np.linspace(-1, 1, width)
        y_coords = np.linspace(-1, 1, height)
        xv, yv = np.meshgrid(x_coords, y_coords)
        vertices = np.stack([xv, yv, z_vals], axis=-1).reshape(-1, 3)
        faces = []
        for i in range(height - 1):
            for j in range(width - 1):
                idx = i * width + j
                idx_right = idx + 1
                idx_bottom = idx + width
                idx_bottom_right = idx_bottom + 1
                faces.append([idx, idx_right, idx_bottom])
                faces.append([idx_right, idx_bottom_right, idx_bottom])
        return vertices, np.array(faces)

    def process(self, image_path, output_path, max_res=500, z_scale=0.5):
        vertices, faces = self._create_height_mesh(image_path, max_res, z_scale)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("# Height map mesh\n")
            f.write(f"v {len(vertices)} {len(faces)}\n")
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
    max_res = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    z_scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    eng = Engine3d()
    eng.process(img_path, out_path, max_res, z_scale)
