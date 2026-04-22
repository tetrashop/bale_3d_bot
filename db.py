import sqlite3
import os
from config import Config
from error_handler import ErrorHandler
class Database:
    def __init__(self, db_path=Config.KNOWLEDGE_DB):
        self.db_path = db_path
        self._ensure_dir()
        def _ensure_dir(self):
            dir_path = os.path.dirname(os.path.abspath(self.db_path))
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                def connect(self):
                    try:
                        return sqlite3.connect(self.db_path)
                    except Exception as e:
                        ErrorHandler.log_error(e)
                        return None
                        def execute(self, query, params=(), commit=False):
                            conn = self.connect()
                            if not conn:
                                return None
                                try:
                                    c = conn.cursor()
                                    c.execute(query, params)
                                    if commit:
                                        conn.commit()
                                        return c
                                    except Exception as e:
                                        ErrorHandler.log
