import numpy as np
import os
import time

def cubic_bezier(p0, p1, p2, p3, t):
    return ((1 - t)**3)*p0 + 3*((1 - t)**2)*t*p1 + 3*(1 - t)*(t**2)*p2 + (t**3)*p3

def generate_closed_curve(control_points, n_points=20):
    curve_points = []
    for i in range(n_points):
        t = i/(n_points - 1)
        pt = cubic_bezier(control_points[0], control_points[1], control_points[2], control_points[3], t)
        curve_points.append(pt)
    # اطمینان از بسته بودن منحنی
    if not np.allclose(curve_points[0], curve_points[-1]):
        curve_points.append(curve_points[0])
    return np.array(curve_points)

def make_faces_between_curves(curve1, curve2):
    faces = []
    n = len(curve1)
    for i in range(n - 1):
        v1 = i + 1
        v2 = i + 2
        v3 = i + 1 + n
        v4 = i + 2 + n
        faces.append((v1, v3, v2))
        faces.append((v2, v3, v4))
    return faces

def aggregate_trapezoids(trapezoids):
    p0s = np.array([tr[0][0] for tr in trapezoids], dtype=float)
    p1s = np.array([tr[0][1] for tr in trapezoids], dtype=float)
    p2s = np.array([tr[1][0] for tr in trapezoids], dtype=float)
    p3s = np.array([tr[1][1] for tr in trapezoids], dtype=float)

    agg_p0 = np.mean(p0s, axis=0)
    agg_p1 = np.mean(p1s, axis=0)
    agg_p2 = np.mean(p2s, axis=0)
    agg_p3 = np.mean(p3s, axis=0)

    return [[agg_p0, agg_p1], [agg_p2, agg_p3]]

class Engine3D:
    def __init__(self):
        self.model_path = None

    def generate_trapezoid_mesh(self, edge1_pts, edge2_pts, output_folder="public/models", base_name=None):
        os.makedirs(output_folder, exist_ok=True)
        if base_name is None:
            base_name = f"trapezoid_{int(time.time())}"

        def control_points(p0, p3):
            p0 = np.array(p0, dtype=float)
            p3 = np.array(p3, dtype=float)
            p1 = p0 + (p3 - p0) * 0.3 + np.array([0, 0, 0.1])
            p2 = p0 + (p3 - p0) * 0.7 + np.array([0, 0, 0.1])
            return np.array([p0, p1, p2, p3])

        cp1 = control_points(edge1_pts[0], edge1_pts[1])
        cp2 = control_points(edge2_pts[0], edge2_pts[1])

        n_points = 30
        curve1 = generate_closed_curve(cp1, n_points)
        curve2 = generate_closed_curve(cp2, n_points)

        vertices = np.vstack((curve1, curve2))
        faces = make_faces_between_curves(curve1, curve2)

        obj_path = os.path.join(output_folder, base_name + ".obj")
        with open(obj_path, "w") as f:
            f.write("# Trapezoid mesh with cubic Bezier edges\n")
            f.write(f"o {base_name}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write("f {} {} {}\n".format(*face))
        self.model_path = obj_path
        return True, obj_path

    def generate_aggregated_model(self, trapezoids, output_folder="public/models"):
        aggregated = aggregate_trapezoids(trapezoids)
        return self.generate_trapezoid_mesh(aggregated[0], aggregated[1], output_folder=output_folder)

if __name__ == "__main__":
    engine = Engine3D()
    trapezoids = [
        [[np.array([0, 0, 0]), np.array([1, 0, 0])], [np.array([0, 1, 0]), np.array([1, 1, 0])]],
        [[np.array([1, 0, 0]), np.array([2, 0, 0])], [np.array([1, 1, 0]), np.array([2, 1, 0])]],
        [[np.array([0, 1, 0]), np.array([1, 1, 0])], [np.array([0, 2, 0]), np.array([1, 2, 0])]],
        [[np.array([1, 1, 0]), np.array([2, 1, 0])], [np.array([1, 2, 0]), np.array([2, 2, 0])]],
    ]
    success, filepath = engine.generate_aggregated_model(trapezoids)
    if success:
        print(f"مدل تجمیع‌شده ذخیره شد در: {filepath}")
    else:
        print("خطا در ساخت مدل تجمیع‌شده")
