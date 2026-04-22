# payment_manager.py
import json
import os
class PaymentManager:
    def __init__(self, filename="payments.json"):
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
                                def add_payment(self, payment_id, payment_info):
                                    data = self._load()
                                    if str(payment_id) in data:
                                        return False
                                        data[str(payment_id)] = payment_info
                                        self._save(data)
                                        return True
                                        def get_payment(self, payment_id):
                                            data = self._load()
                                            return data.get(str(payment_id))
                                            def update_payment(self, payment_id, payment_info):
                                                data = self._load()
                                                if str(payment_id) not in data:
                                                    return False
                                                    data[str(payment_id)].update(payment_info)
                                                    self._save(data)
                                                    return True
