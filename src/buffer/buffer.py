import asyncio
from typing import Optional
from src.core.models import LogEntry

class LogBuffer:
    def __init__(self, max_size: int = 1000):
        self._queue = asyncio.Queue(maxsize=max_size)
        self.dropped_count = 0

    async def push(self, entry: LogEntry) -> None:
        """
        Pushes an entry into the buffer. 
        If full, it evicts the oldest entry (Circular Logic).
        """
        if self._queue.full():
            try:
                # Evict oldest to maintain NFR-2 (Minimal Footprint)
                self._queue.get_nowait()
                self.dropped_count += 1
            except asyncio.QueueEmpty:
                pass
        
        await self._queue.put(entry)

    async def pop(self) -> LogEntry:
        """Pulls the next available entry from the buffer."""
        return await self._queue.get()

    def qsize(self) -> int:
        return self._queue.qsize()

    def task_done(self) -> None:
        self._queue.task_done()