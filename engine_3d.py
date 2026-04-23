# engine_3d.py
import os
import time
import numpy as np
from PIL import Image

class Engine3D:
    def __init__(self):
        self.model_path = None
        self.vertices = []
        self.faces = []

    def cubic_bezier(self, p0, p1, p2, p3, t):
        return ((1 - t)**3)*p0 + 3*((1 - t)**2)*t*p1 + 3*(1 - t)*(t**2)*p2 + (t**3)*p3

    def generate_closed_curve(self, control_points, num_points=20):
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            points.append(self.cubic_bezier(control_points[0], control_points[1], control_points[2], control_points[3], t))
        if not np.allclose(points[0], points[-1]):
            points.append(points[0])
        return np.array(points)

    def make_faces_between_curves(self, curve1, curve2):
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

    def generate_trapezoid_mesh(self, edge1_pts, edge2_pts, base_name=None, output_dir="models"):
        os.makedirs(output_dir, exist_ok=True)
        if base_name is None:
            base_name = f"model_{int(time.time())}"
        
        def control_points(p0, p3):
            p1 = p0 + (p3 - p0) * 0.3 + np.array([0,0,0.1])
            p2 = p0 + (p3 - p0) * 0.7 + np.array([0,0,0.1])
            return np.array([p0, p1, p2, p3])

        cp1 = control_points(edge1_pts[0], edge1_pts[1])
        cp2 = control_points(edge2_pts[0], edge2_pts[1])

        curve1 = self.generate_closed_curve(cp1)
        curve2 = self.generate_closed_curve(cp2)

        vertices = np.vstack((curve1, curve2))
        faces = self.make_faces_between_curves(curve1, curve2)

        obj_path = os.path.join(output_dir, base_name + ".obj")
        with open(obj_path, "w") as f:
            f.write("# Generated trapezoid mesh\n")
            f.write(f"o {base_name}\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for face in faces:
                f.write(f"f {face[0]} {face[1]} {face[2]}\n")
        
        self.model_path = obj_path
        return True, obj_path

    def generate_aggregated_model(self, trapezoids, output_dir="models"):
        aggregated = self.aggregate_trapezoids(trapezoids)
        return self.generate_trapezoid_mesh(aggregated[0], aggregated[1], output_dir=output_dir)


# test.py
from engine_3d import Engine3D
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

def test_model_generation():
    engine = Engine3D()
    trapezoids = [
        [[np.array([0,0,0]), np.array([1,0,0])], [np.array([0,1,0]), np.array([1,1,0])]],
        [[np.array([1,0,0]), np.array([2,0,0])], [np.array([1,1,0]), np.array([2,1,0])]],
        [[np.array([0,1,0]), np.array([1,1,0])], [np.array([0,2,0]), np.array([1,2,0])]],
        [[np.array([1,1,0]), np.array([2,1,0])], [np.array([1,2,0]), np.array([2,2,0])]],
    ]
    success, path = engine.generate_aggregated_model(trapezoids)
    if success:
        logger.info(f"مدل ساخته شد: {path}")
    else:
        logger.error("خطا در ساخت مدل")
    return path if success else None

if __name__ == "__main__":
    test_model_generation()
