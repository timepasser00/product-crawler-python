from collections import deque
from urllib.parse import urlparse
from typing import Set, Tuple

SKIP_EXTENSIONS = (".jpg", ".png", ".svg", ".js", ".css", ".ico", ".woff", ".ttf", ".mp4", ".pdf", ".zip")
SKIP_PATH_KEYWORDS = ("/login", "/signup", "/cart", "/help", "/terms", "/privacy", "/account")

class URLFrontier:
    def __init__(self, seed_url: str, max_depth: int = 3):
        self.queue = deque()  # (url, depth)
        self.visited: Set[str] = set()
        self.allowed_domain = urlparse(seed_url).netloc
        self.max_depth = max_depth

    def is_valid_url(self, url: str, depth: int) -> bool:
        parsed = urlparse(url)
        path = parsed.path.lower()

        return (
            parsed.scheme in ("http", "https") and
            parsed.netloc == self.allowed_domain and
            not url.endswith(SKIP_EXTENSIONS) and
            not any(skip in path for skip in SKIP_PATH_KEYWORDS) and
            depth <= self.max_depth and
            url not in self.visited
        )

    def add_urls(self, urls: Set[str], current_depth: int):
        next_depth = current_depth + 1
        for url in urls:
            if self.is_valid_url(url, next_depth):
                self.queue.append((url, next_depth))
                self.visited.add(url)

    def has_next(self) -> bool:
        return len(self.queue) > 0

    def next_url(self) -> Tuple[str, int]:
        return self.queue.popleft()
    