from urllib.parse import urlparse
from typing import Set
import asyncio

from product_url_analyser import is_dead_end_url, is_product_url

SKIP_EXTENSIONS = (".jpg", ".png", ".svg", ".js", ".css", ".ico", ".woff", ".ttf", ".mp4", ".pdf", ".zip")
SKIP_PATH_KEYWORDS = ("/login", "/signup", "/cart", "/help", "/terms", "/privacy", "/account")

class URLFrontier:
    def __init__(self, seed_url: str, max_depth: int = 3):
        self.queue = asyncio.PriorityQueue()
        self.visited: Set[str] = set()
        self.allowed_domain = urlparse(seed_url).netloc
        self.max_depth = max_depth
        self.condition = asyncio.Condition()


    def has_next(self) -> bool:
        return len(self.queue) > 0

    async def add_urls(self, urls: set[str], current_depth: int):
        async with self.condition:
            for url in urls:
                if url not in self.visited and current_depth + 1 <= self.max_depth:
                    self.visited.add(url)
                    priority = self.score_url(url)
                    await self.queue.put((priority, url, current_depth + 1))
            self.condition.notify_all()

    async def next_url(self):
        async with self.condition:
            while self.queue.empty():
                await self.condition.wait()
            priority, url, depth = await self.queue.get()
            return url, depth

    def is_empty(self):
        return self.queue.empty()
    
    def score_url(self, url: str) -> int:

        is_prod_url, score , explanation = is_product_url(url)
        
        # High confidence product indicators
        if is_prod_url and score > 1:
            return 1

        # Medium confidence: numeric slug or long URLs
        if is_prod_url and score >= 0:
            return 3

        # Known non-product paths
        if is_dead_end_url(url):
            return 100

        # Default
        return 10

    