from worker import start_worker, submit_job
from db import init_db, save_job, get_job
import time
import os
def bot_send_result(user_id, job_id, output_path):
    print(f"[RESULT] user_id={user_id} job_id={job_id} output_path={output_path}")
    print("[TEST] starting worker...")
    init_db()
    start_worker(bot_send_result)
    print("[TEST] creating job...")
    save_job("job1", 123, "test.txt", "test.txt")
    submit_job({"job_id": "job1", "user_id": 123, "input_path": "test.txt"})
    print("[TEST] job submitted, waiting...")
    time.sleep(5)
    print("[TEST] finished")
    print("[TEST] job row:")
    job = get_job("job1")
    if job:
        print(job["job_id"], job["user_id"], job["status"], job["output_path"])
        print("[TEST] files now:")
        for name in sorted(os.listdir(".")):
            if "test" in name or "output" in name or "processed" in name:
                print(" -", name)
