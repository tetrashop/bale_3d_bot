import sys
import os
import numpy as np
from PIL import Image

def image_to_3d_mesh(image_path, output_obj="public/models/3d_object.obj", max_size=200):
    img = Image.open(image_path).convert("L")
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    image = np.array(img)
    h, w = image.shape

    vertices = []
    for y in range(h):
        for x in range(w):
            z = image[y, x] / 255.0
            vertices.append((float(x) / w, float(y) / h, z))

    faces = []
    def vertex_id(x, y):
        return y*w + x + 1

    for y in range(h-1):
        for x in range(w-1):
            v1 = vertex_id(x, y)
            v2 = vertex_id(x+1, y)
            v3 = vertex_id(x, y+1)
            v4 = vertex_id(x+1, y+1)
            faces.append((v1, v2, v3))
            faces.append((v3, v2, v4))

    os.makedirs(os.path.dirname(output_obj), exist_ok=True)
    with open(output_obj, "w") as f:
        f.write("# Generated 3D mesh from grayscale image\n")
        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")

    print(f"Model saved to {output_obj}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python engine_3d.py <input_image> <output_obj>")
        sys.exit(1)
    input_image = sys.argv[1]
    output_obj = sys.argv[2]
    image_to_3d_mesh(input_image, output_obj)
