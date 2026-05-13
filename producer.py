import multiprocessing
import time
import json
import random
import sys

# --- PRODUCER CONFIG ---
PRODUCER_PROFILES = {
    "auth-service": {"delay": 0.005, "error_rate": 0.2, "levels": ["INFO", "WARN", "ERROR"]},
    "api-gateway":  {"delay": 0.01,  "error_rate": 0.1, "levels": ["DEBUG", "INFO", "WARN"]},
    "db-cluster":   {"delay": 0.05,  "error_rate": 0.05, "levels": ["INFO", "ERROR"]}
}

def run_producer(name, profile):
    messages = ["Connection refused", "Unauthorized access", "Memory limit reached", "Disk I/O high"]
    while True:
        log = {
            "timestamp": time.time(),
            "level": random.choice(profile["levels"]),
            "service": name,
            "message": random.choice(messages),
            #"request_id": f"REQ-{random.randint(1000, 9999)}" # To test ID ignoring later
        }
        sys.stdout.write(json.dumps(log) + "\n")
        sys.stdout.flush()
        time.sleep(profile["delay"])

if __name__ == "__main__":
    processes = []
    for name, profile in PRODUCER_PROFILES.items():
        p = multiprocessing.Process(target=run_producer, args=(name, profile))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()