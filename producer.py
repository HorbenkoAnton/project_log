import multiprocessing
import time
import json
import random
import sys
import uuid

# --- PRODUCER CONFIG ---
PRODUCER_PROFILES = {
    # Existing "Generic" behavior
    "auth-service": {"delay": 0.009, "mode": "generic", "levels": ["CRITICAL", "INFO", "WARN", "ERROR"]},
    "api-gateway":  {"delay": 0.01,  "mode": "generic", "levels": ["DEBUG", "INFO", "WARN"]},
    "db-service":   {"delay": 0.007, "mode": "generic", "levels": ["ERROR", "WARN","CRITICAL"]},
    
    # Specific Masking Tests
    # "id-service":    {"delay": 0.002, "mode": "id",      "levels": ["ERROR"]},
    # "net-service":   {"delay": 0.005, "mode": "ip",      "levels": ["INFO"]},
    # "txn-service":   {"delay": 0.003, "mode": "uuid",    "levels": ["WARN"]},
    # "pointer-service":{"delay": 0.004, "mode": "hex",     "levels": ["ERROR", "WARN"]}
}

def generate_noise(mode):
    if mode == "id":
        return str(random.randint(1000, 9999))
    elif mode == "ip":
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
    elif mode == "uuid":
        return str(uuid.uuid4())
    elif mode == "hex":
        return f"0x{random.getrandbits(16):x}"
    return "" # Generic mode adds no extra noise here

def run_producer(name, profile):
    mode = profile.get("mode", "generic")
    
    # Generic message pool
    generic_messages = [
        "Connection refused", 
        "Unauthorized access", 
        "Memory limit reached", 
        "Disk I/O high"
    ]
    
    # Specific templates for masking tests
    templates = {
        "id": "Failed login for user",
        "ip": "Connection blocked from",
        "uuid": "Transaction error",
        "hex": "Pointer error at"
    }

    while True:
        if mode == "generic":
            msg = random.choice(generic_messages)
        else:
            base = templates.get(mode, "System notification")
            msg = f"{base} {generate_noise(mode)}"

        log = {
            "timestamp": time.time(),
            "level": random.choice(profile["levels"]),
            "service": name,
            "message": msg
        }
        
        #print(json.dumps(log))
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