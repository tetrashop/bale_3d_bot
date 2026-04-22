from engine_3d import Engine3D
from error_handler import ErrorHandler
class ImageHelper:
    def __init__(self):
        self.engine = Engine3D()
        def process_images(self, images):
            try:
                return self.engine.process_images(images)
            except Exception as e:
                ErrorHandler.log_error(e)
                return None
