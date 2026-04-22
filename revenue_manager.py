# revenue_manager.py
import os
import json
import threading
class RevenueManager:
    def __init__(self, filename="balances.json"):
        self.filename = filename
        self.lock = threading.Lock()
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump({}, f)
                def _load(self):
                    with open(self.filename, "r") as f:
                        return json.load(f)
                        def _save(self, data):
                            with open(self.filename, "w") as f:
                                json.dump(data, f, indent=2)
                                def get_balance(self, user_id):
                                    with self.lock:
                                        data = self._load()
                                        return data.get(str(user_id), 0)
                                        def increase_balance(self, user_id, amount):
                                            with self.lock:
                                                data = self._load()
                                                user_key = str(user_id)
                                                data[user_key] = data.get(user_key, 0) + amount
                                                self._save(data)
                                                return data[user_key]
                                                def decrease_balance(self, user_id, amount):
                                                    with self.lock:
                                                        data = self._load()
                                                        user_key = str(user_id)
                                                        current = data.get(user_key, 0)
                                                        if current < amount:
                                                            return False
                                                            data[user_key] = current - amount
                                                            self._save(data)
                                                            return True
