import asyncio
from src.ingestion.stream import get_stream
from src.ingestion.validator import validate_log
from src.buffer.buffer import LogBuffer

# Configuration for Burst Testing
BUFFER_SIZE = 10
buffer = LogBuffer(max_size=BUFFER_SIZE)

async def ingestor_task():
    """Continuously fills the buffer."""
    print(f"--- Ingestor: Filling buffer (Target: {BUFFER_SIZE}) ---", flush=True)
    
    # Using a simple loop; if it blocks, we use the executor fix from before
    for raw_line in get_stream():
        entry, success = validate_log(raw_line)
        if success and entry:
            await buffer.push(entry)
            # Log progress so we know it's working
            print(f"Ingestor: Added log. Buffer size: {buffer.qsize()}", flush=True)
        
        # Give the event loop a tiny break to allow other tasks to check conditions
        await asyncio.sleep(0)

async def engine_task():
    """Waits for a full buffer, then dumps everything."""
    print("--- Engine: Waiting for full buffer ---", flush=True)
    
    while True:
        # 1. Wait until the buffer hits the limit
        if buffer.qsize() < BUFFER_SIZE:
            await asyncio.sleep(0.1) # Check every 100ms
            continue
        
        # 2. Trigger the Burst
        print(f"\n--- BUFFER FULL ({BUFFER_SIZE}): STARTING BURST ---", flush=True)
        
        while buffer.qsize() > 0:
            log = await buffer.pop()
            print(f"Engine Processed: {log.message}")
            buffer.task_done()
            
        print("--- BURST COMPLETE: Buffer is empty ---\n", flush=True)

async def main():
    await asyncio.gather(ingestor_task(), engine_task())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest stopped.")

#set's up buffer queue size of 10
#fristly turns on producer to generate a stream
#then catches stream with get_stream and 
#passes those line to validate_log()
#then validated logs are getting into buffer
#when buffer is full it's just sudenly print all 10 elements which are in buffer