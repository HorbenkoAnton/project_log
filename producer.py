# import json
# import sys
# import time
# import random

# def generate_logs():
#     # Matches requirements in ARCHITECTURE.md
#     levels = ["ERROR", "WARN", "INFO", "DEBUG"]
#     services = ["auth-service", "db-cluster-01", "api-gateway"]
#     messages = [
#         "Connection refused by database",
#         "Unauthorized access attempt",
#         "Memory limit reached",
#         "Disk I/O latency high",
#         "Invalid API key provided"
#     ]
    
#     while True:
#         log = {
#             "timestamp": time.time(),
#             "level": random.choice(levels),
#             "service": random.choice(services),
#             "message": random.choice(messages)
#         }
#         # Writing to stdout creates the 'Source' of the stream
#         sys.stdout.write(json.dumps(log) + "\n")
#         sys.stdout.flush() 
        
#         # Simulate traffic spikes for NFR-1
#         time.sleep(random.uniform(0.01, 0.2))

# if __name__ == "__main__":
#     generate_logs()

import json
import sys
import time
import random

def generate_test_logs():
    services = ["auth-service", "api-gateway"]
    levels = ["ERROR", "WARN", "INFO", "DEBUG"]
    services = ["auth-service", "db-cluster-01", "api-gateway"]
    messages = [
        "Connection refused by database",
        "Unauthorized access attempt",
        "Memory limit reached",
        "Disk I/O latency high",
        "Invalid API key provided"
    ]


    while True:
        # 1. Randomly decide if this log will be "Good" or "Bad"
        is_valid = random.choice([True, False])
        
        if is_valid:
            # Matches your LogEntry schema
            log = {
                "timestamp": time.time(),
                "level": random.choice(levels),
                "service": random.choice(services),
                "message": random.choice(messages)
            }
        else:
            # 2. Generate a "Bad" log (Missing fields or wrong types)
            bad_scenarios = [
                {"msg": "Missing level and timestamp"}, # Missing keys
                {"level": 123, "message": "Wrong type for level"}, # Type error
                "This is not even JSON", # Structural error
                {"level": "WARN", "message": "Missing service"} # Schema violation
            ]
            log = random.choice(bad_scenarios)

        # 3. Stream out
        if isinstance(log, dict):
            output = json.dumps(log)
        else:
            output = log # Send raw string for "This is not even JSON" case
            
        sys.stdout.write(output + "\n")
        sys.stdout.flush() 
        
        time.sleep(0.1)

if __name__ == "__main__":
    generate_test_logs()