import sys
import os
import logging
import numpy as np

sys.path.append(".")

from engine_3d import Engine3D

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

def test_model_generation():
    engine = Engine3D()
    edge1 = [np.array([0, 0, 0]), np.array([1, 0, 0])]
    edge2 = [np.array([0, 1, 0]), np.array([1, 1, 0])]
    success, filepath = engine.generate_trapezoid_mesh(edge1, edge2)
    if success:
        logger.info(f"مدل ساخته شده: {filepath}")
        return filepath
    else:
        logger.error("خطا در ساخت مدل")
        return None

if __name__ == "__main__":
    logger.info("شروع تست ساخت مدل")
    test_model_generation()
