import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    MODEL_3D_PATH = os.getenv("MODEL_3D_PATH", "./models")
    PAYMENT_DB = os.getenv("PAYMENT_DB", "./payment.db")
    KNOWLEDGE_DB = os.getenv("KNOWLEDGE_DB", "./knowledge.db")
    LOG_PATH = os.getenv("LOG_PATH", "./logs/app.log")
    CHECK_ONLINE = os.getenv("CHECK_ONLINE", "True").lower() in ("true", "1", "yes")
