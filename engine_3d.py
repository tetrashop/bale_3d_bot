import os
import sys
import time
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None
        self.vertices = []

    def image_to_3d_spherical(self, image_path, output_obj="public/models/3d_object.obj", max_res=300):
        img = Image.open(image_path).convert("L")
        img.thumbnail((max_res, max_res), Image.LANCZOS)
        image = np.array(img)

        h, w = image.shape
        cx, cy = w / 2, h / 2
        max_r = np.sqrt(cx ** 2 + cy ** 2)

        self.vertices = []
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
                self.vertices.append((X, Y, Z))

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

                if is_valid_triangle(self.vertices[v1 - 1], self.vertices[v2 - 1], self.vertices[v3 - 1]):
                    faces.append((v1, v2, v3))
                if is_valid_triangle(self.vertices[v3 - 1], self.vertices[v2 - 1], self.vertices[v4 - 1]):
                    faces.append((v3, v2, v4))

        os.makedirs(os.path.dirname(output_obj), exist_ok=True)
        with open(output_obj, "w") as f:
            f.write("# OBJ model with lighting-based depth and valid triangles\n")
            for v in self.vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")

        self.model_path = output_obj
        print(f"مدل سه‌بعدی در فایل {output_obj} ذخیره شد.")
        return True, output_obj

    def cubic_bezier(self, p0, p1, p2, p3, t):
        return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * (t ** 2) * p2 + (t ** 3) * p3

    def generate_closed_curve(self, control_points, num_points=20):
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            points.append(self.cubic_bezier(control_points[0], control_points[1], control_points[2], control_points[3], t))
        if not np.allclose(points[0], points[-1]):
            points.append(points[0])
        return np.array(points)

    def aggregate_trapezoids(self, trapezoids):
        p0s = np.array([t[0][0] for t in trapezoids], dtype=float)
        p1s = np.array([t[0][1] for t in trapezoids], dtype=float)
        p2s = np.array([t[1][0] for t in trapezoids], dtype=float)
        p3s = np.array([t[1][1] for t in trapezoids], dtype=float)

        agg_p0 = np.mean(p0s, axis=0)
        agg_p1 = np.mean(p1s, axis=0)
        agg_p2 = np.mean(p2s, axis=0)
        agg_p3 = np.mean(p3s, axis=0)

        return [[agg_p0, agg_p1], [agg_p2, agg_p3]]

    def generate_trapezoid_mesh(self, edge1_pts, edge2_pts, base_name=None, output_dir="public/models"):
        os.makedirs(output_dir, exist_ok=True)
        if base_name is None:
            base_name = f"model_{int(time.time())}"

        def control_points(p0, p3):
            p1 = p0 + (p3 - p0) * 0.3 + np.array([0, 0, 0.1])
            p2 = p0 + (p3 - p0) * 0.7 + np.array([0, 0, 0.1])
            return np.array([p0, p1, p2, p3])

        cp1 = control_points(edge1_pts[0], edge1_pts[1])
        cp2 = control_points(edge2_pts[0], edge2_pts[1])

        curve1 = self.generate_closed_curve(cp1)
        curve2 = self.generate_closed_curve(cp2)

        vertices = np.vstack((curve1, curve2))

        faces = []
        n = len(curve1)
        for i in range(n - 1):
            faces.append((i + 1, i + 1 + n, i + 2))
            faces.append((i + 2, i + 1 + n, i + 2 + n))

        obj_path = os.path.join(output_dir, base_name + ".obj")
        with open(obj_path, "w") as f:
            f.write("# Trapezoid mesh with cubic Bezier edges\n")
            f.write(f"o {base_name}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")

        self.model_path = obj_path
        print(f"مدل ذوذنقه در {obj_path} ذخیره شد.")
        return True, obj_path

    def generate_aggregated_model(self, trapezoids, output_dir="public/models"):
        aggregated = self.aggregate_trapezoids(trapezoids)
        return self.generate_trapezoid_mesh(aggregated[0], aggregated[1], output_dir=output_dir)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        input_image_path = sys.argv[1]
        output_obj_path = sys.argv[2]
        engine = Engine3D()
        engine.image_to_3d_spherical(input_image_path, output_obj_path)
    else:
        engine = Engine3D()
        trapezoids = [
            [[np.array([0, 0, 0]), np.array([1, 0, 0])], [np.array([0, 1, 0]), np.array([1, 1, 0])]],
            [[np.array([1, 0, 0]), np.array([2, 0, 0])], [np.array([1, 1, 0]), np.array([2, 1, 0])]],
            [[np.array([0, 1, 0]), np.array([1, 1, 0])], [np.array([0, 2, 0]), np.array([1, 2, 0])]],
            [[np.array([1, 1, 0]), np.array([2, 1, 0])], [np.array([1, 2, 0]), np.array([2, 2, 0])]],
        ]
        success, path = engine.generate_aggregated_model(trapezoids)
        if success:
            print(f"مدل تجمیع‌شده ذخیره شد در: {path}")
        else:
            print("خطا در ساخت مدل")
