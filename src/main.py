from ingestion.stream import get_stream
from ingestion.validator import validate_log

def run_test_pipeline():
    print("--- Pipeline Testing Mode ---", flush=True)
    
    processed_count = 0
    dropped_count = 0

    # Step 1: Catch logs from the stream generator
    for raw_line in get_stream():
        
        # Step 2: Validate the line
        log_entry, success = validate_log(raw_line)
        
        if success and log_entry:
            processed_count += 1
            # Current output for testing connectivity
            print(f"Valid: [{log_entry.level}] {log_entry.message} ({log_entry.service})", flush=True)
        else:
            dropped_count += 1
            print(f"Dropped: Invalid log format or missing fields", flush=True)

        # Print stats every 10 logs to monitor health
        if (processed_count + dropped_count) % 10 == 0:
            print(f"--- Stats: Processed {processed_count} | Dropped {dropped_count} ---", flush=True)

if __name__ == "__main__":
    run_test_pipeline()