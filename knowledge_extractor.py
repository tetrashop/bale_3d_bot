import sqlite3
import os
from utils import is_online
from error_handler import ErrorHandler
from config import Config
class KnowledgeExtractor:
    def __init__(self, db_path=Config.KNOWLEDGE_DB):
        self.db_path = db_path
        self.online = Config.CHECK_ONLINE and is_online()
        self._init_db()
        def _init_db(self):
            try:
                if not os.path.exists(self.db_path):
                    with sqlite3.connect(self.db_path) as conn:
                        c = conn.cursor()
                        c.execute("""
                        CREATE TABLE knowledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE,
                        value TEXT
                        )
                        """)
                        conn.commit()
                    except Exception as e:
                        ErrorHandler.log_error(e)
                        def add_knowledge(self, key, value):
                            try:
                                with sqlite3.connect(self.db_path) as conn:
                                    c = conn.cursor()
                                    c.execute(
                                    "INSERT OR REPLACE INTO knowledge (key, value) VALUES (?, ?)",
                                    (key, value),
                                    )
                                    conn.commit()
                                except Exception as e:
                                    ErrorHandler.log_error(e)
                                    def extract(self, data):
                                        try:
                                            if self.online:
                                                ErrorHandler.log_info("Online knowledge extraction placeholder")
                                                # TODO: استخراج دانش آنلاین در صورت امکان
                                                for k, v in data.items():
                                                    self.add_knowledge(k, str(v))
                                                except Exception as e:
                                                    ErrorHandler.log_error(e)
                                                    def query_knowledge(self, key):
                                                        try:
                                                            with sqlite3.connect(self.db_path) as conn:
                                                                c = conn.cursor()
                                                                c.execute("SELECT value FROM knowledge WHERE key=?", (key,))
                                                                row = c.fetchone()
                                                                return row[0] if row else None
                                                            except Exception as e:
                                                                ErrorHandler.log_error(e)
                                                                return None
