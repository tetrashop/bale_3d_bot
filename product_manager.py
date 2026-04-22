# product_manager.py
import json
import os
class ProductManager:
    def __init__(self, filename="products.json"):
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
                                def add_product(self, product_id, product_info):
                                    data = self._load()
                                    if str(product_id) in data:
                                        return False
                                        data[str(product_id)] = product_info
                                        self._save(data)
                                        return True
                                        def get_product(self, product_id):
                                            data = self._load()
                                            return data.get(str(product_id))
                                            def update_product(self, product_id, product_info):
                                                data = self._load()
                                                if str(product_id) not in data:
                                                    return False
                                                    data[str(product_id)].update(product_info)
                                                    self._save(data)
                                                    return True
