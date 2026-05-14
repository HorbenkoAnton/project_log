import asyncio
import sys
from notification.notification_controller import NotificationController
import src.config as config
from src.ingestion.stream import get_stream
from src.ingestion.validator import validate_log
from src.buffer.buffer import LogBuffer
from src.engine.aggregator import AggregationEngine
from reporting.reporter import Reporter

async def ingestor_task(buffer: LogBuffer):
    """Reads raw lines and pushes immediately to the buffer."""
    loop = asyncio.get_running_loop()
    
    def threaded_stream():
        # Producer -> stdin -> get_stream
        for raw_line in get_stream():
            # Offload raw string to buffer
            asyncio.run_coroutine_threadsafe(buffer.push(raw_line), loop)
            #print(f"Buffer size: {buffer._queue.qsize()}", end="\n", flush=True)

    await loop.run_in_executor(None, threaded_stream)

async def worker_task(buffer: LogBuffer, engine: AggregationEngine):
    """Pulls raw data from buffer, validates, and aggregates."""
    print("--- Worker: Processing logs ---", flush=True)
    while True:
        raw_line = await buffer.pop()
        
        # Validation happens here to keep ingestor non-blocking
        entry, success = validate_log(raw_line)
        
        if success and entry:
            engine.process(entry)
            #print(f"Processed: {entry.message}") 
        
        buffer.task_done()

async def reporter_task(engine: AggregationEngine, reporter: Reporter):
    controller = NotificationController()
    
    while True:
        await asyncio.sleep(5)
        
        should_send, trigger = controller.check_trigger(
            engine.total_processed, 
            len(engine.registry)
        )
        
        if should_send:
            report_data = engine.flush_report()
            if report_data:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, reporter.send_report, report_data)
                controller.mark_sent(engine.total_processed, trigger)

async def monitor_task(engine: AggregationEngine):
    """Prints processing stats every 5 seconds."""
    last_count = 0
    while True:
        await asyncio.sleep(5)
        
        current_count = engine.total_processed
        delta = current_count - last_count
        logs_per_sec = delta / 5
        
        print(f"--- Stats: {current_count} total logs | {logs_per_sec:.2f} logs/sec ---", flush=True)
        last_count = current_count


async def main():
    print("--- APP STARTING ---", flush=True)
    
    # Initialization inside main to prevent import side-effects
    shared_buffer = LogBuffer(max_size=config.BUFFER_SIZE)
    shared_engine = AggregationEngine(mask_ids=config.MASK_IDS)
    shared_reporter = Reporter()

    try:
        await asyncio.gather(
            ingestor_task(shared_buffer),
            worker_task(shared_buffer, shared_engine),
            reporter_task(shared_engine, shared_reporter),
            monitor_task(shared_engine)
        )
    except Exception as e:
        sys.stderr.write(f"CRITICAL CRASH: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())