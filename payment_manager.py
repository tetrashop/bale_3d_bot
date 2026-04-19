import sqlite3
from datetime import datetime
from utils import is_online
from error_handler import ErrorHandler
from config import Config


class PaymentManager:
    def __init__(self, db_path=Config.PAYMENT_DB):
        self.db_path = db_path
        self.online = Config.CHECK_ONLINE and is_online()
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    date TEXT,
                    status TEXT
                )
                """)
                conn.commit()
        except Exception as e:
            ErrorHandler.log_error(e)

    def record_payment(self, amount, status="pending"):
        try:
            if self.online:
                ErrorHandler.log_info("Online payment processing placeholder")
                # TODO: ارسال پرداخت به سرور آنلاین یا API
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO payments (amount, date, status) VALUES (?, ?, ?)",
                    (amount, datetime.utcnow().isoformat(), status),
                )
                conn.commit()
                return c.lastrowid
        except Exception as e:
            ErrorHandler.log_error(e)
            ErrorHandler.fallback_operation()
            return None

    def update_payment_status(self, payment_id, status):
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "UPDATE payments SET status=? WHERE id=?", (status, payment_id)
                )
                conn.commit()
        except Exception as e:
            ErrorHandler.log_error(e)
