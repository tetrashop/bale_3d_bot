# inventory_manager.py
import json
import os
class InventoryManager:
    def __init__(self, filename="inventory.json"):
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
                                def add_item(self, item_id, item_info):
                                    data = self._load()
                                    if str(item_id) in data:
                                        return False
                                        data[str(item_id)] = item_info
                                        self._save(data)
                                        return True
                                        def get_item(self, item_id):
                                            data = self._load()
                                            return data.get(str(item_id))
                                            def update_item(self, item_id, item_info):
                                                data = self._load()
                                                if str(item_id) not in data:
                                                    return False
                                                    data[str(item_id)].update(item_info)
                                                    self._save(data)
                                                    return True
