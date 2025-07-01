import asyncio


class WorkTracker:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.count = 0
        self.event = asyncio.Event()
        self.event.clear()

    async def add(self, n=1):
        async with self.lock:
            self.count += n
            self.event.clear()

    async def done(self, n=1):
        async with self.lock:
            self.count -= n
            if self.count == 0:
                self.event.set()

    async def wait(self):
        await self.event.wait()
