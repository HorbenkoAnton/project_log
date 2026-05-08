import asyncio
from typing import Optional

class LogBuffer:
    def __init__(self, max_size: int = 1000):
        # Stores raw strings from the stream
        self._queue = asyncio.Queue(maxsize=max_size)
        self.dropped_count = 0

    async def push(self, raw_line: str) -> None:
        """
        Pushes a raw log line into the buffer. 
        If full, evicts the oldest line to maintain NFR-2.
        """
        if self._queue.full():
            try:
                self._queue.get_nowait()
                self.dropped_count += 1
            except asyncio.QueueEmpty:
                pass
        
        await self._queue.put(raw_line)

    async def pop(self) -> str:
        """Pulls the next raw string for validation and processing."""
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()