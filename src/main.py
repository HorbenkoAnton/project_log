import asyncio
from src.ingestion.stream import get_stream
from src.ingestion.validator import validate_log
from src.buffer.buffer import LogBuffer
from src.engine.aggregator import AggregationEngine
import src.config as config

# Configuration for Burst Testing
BUFFER_SIZE = 10
buffer = LogBuffer(max_size=config.BUFFER_SIZE)
engine = AggregationEngine()


async def ingestor_task():
    print(f"--- Ingestor: Filling buffer (Target: {config.BUFFER_SIZE}) ---", flush=True)
    loop = asyncio.get_running_loop()
    
    # We run the blocking generator in a separate thread so the loop can breathe
    def threaded_stream():
        for raw_line in get_stream():
            print("line: " + raw_line + " is added to buffer")
            asyncio.run_coroutine_threadsafe(buffer.push(raw_line), loop)
            
            

    await loop.run_in_executor(None, threaded_stream)

    
async def worker_task():
    """Pulls from buffer, validates, and aggregates."""
    while True:
        raw_line = await buffer.pop()

        # Step 2 & 3: Validate and then Process
        entry, success = validate_log(raw_line)
        
        if success and entry:
            engine.process(entry)
            print("entry: " + str(entry) + " is processed by engine")        
        buffer.task_done()



async def main():
    print(f"--- APP STARTING ---", flush=True)
    try:
        await asyncio.gather(
            ingestor_task(), 
            worker_task()
        )
    except Exception as e:
        print(f"CRITICAL CRASH: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())