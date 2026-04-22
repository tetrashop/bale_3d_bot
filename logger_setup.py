import logging
from config import Config
import os
def setup_logger():
    log_dir = os.path.dirname(Config.LOG_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        logging.basicConfig(
        filename=Config.LOG_PATH,
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s",
        )
        setup_logger()
