# payment_manager.py
import uuid
import threading
class PaymentManager:
    def __init__(self):
        self.payments = {}
        self.lock = threading.Lock()
        def record_payment(self, amount):
            pay_id = str(uuid.uuid4())
            with self.lock:
                self.payments[pay_id] = {"amount": amount, "status": "pending"}
                # فرض بر این است که در اینجا پرداخت به سیستم بانکی ارسال شود و موفقیت ثبت شود.
                # برای سادگی مستقیم موفقیت شبیهسازی میشود.
                with self.lock:
                    self.payments[pay_id]["status"] = "completed"
                    return pay_id
                    def check_payment_status(self, pay_id):
                        with self.lock:
                            return self.payments.get(pay_id, {}).get("status", "not_found")
