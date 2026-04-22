# order_manager.py
import json
import os
class OrderManager:
    def __init__(self, filename="orders.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump({}, f)
                def _load(self):
                    with open(self.filename, "r") as f:
                        return json.load(f)
                        def _save(self, data):
                            with open(self.filename, "w") as f:
                                json.dump(data, f, indent=2)
                                def add_order(self, order_id, order_info):
                                    data = self._load()
                                    if str(order_id) in data:
                                        return False
                                        data[str(order_id)] = order_info
                                        self._save(data)
                                        return True
                                        def get_order(self, order_id):
                                            data = self._load()
                                            return data.get(str(order_id))
                                            def update_order(self, order_id, order_info):
                                                data = self._load()
                                                if str(order_id) not in data:
                                                    return False
                                                    data[str(order_id)].update(order_info)
                                                    self._save(data)
                                                    return True
