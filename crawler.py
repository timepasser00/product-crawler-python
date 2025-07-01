import asyncio
import csv
from urllib.parse import urlparse
import aiofiles
from async_fetcher import AsyncFetcher
from html_parser import HTMLParser
from url_frontier import URLFrontier
from logger_config import setup_logger
from threading import Lock
from work_tracker import WorkTracker

class AsyncCrawler:
    CONCURRENT_FETCHERS = 5

    def __init__(self, output_csv: str = "product_urls.csv"):
        self.html_queue = asyncio.Queue()
        self.logger = None
        self.tracker = None
        self.outputLock = None
        self.output_csv = output_csv
        # Write header to output file
        with open(self.output_csv, mode="w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["seed_domain", "product_url"])

    async def __parser_worker(self, seed_domain: str, frontier: URLFrontier, collected: list[tuple[str, str]]):
        print(f"Parser worker started for domain {seed_domain}")
        html_parser = HTMLParser()
        while True:
            item = await self.html_queue.get()
            if item is None:
                self.html_queue.task_done()
                break
            try:
                url, html, depth = item
                child_urls, product_urls = html_parser.parse_html(url, html, seed_domain)
                print(f"Parsed {len(child_urls)} child URLs and {len(product_urls)} product URLs from {url}")
                await frontier.add_urls(set(child_urls), current_depth=depth)
                for purl in product_urls:
                    with self.outputLock:
                        async with aiofiles.open(self.output_csv, mode="a", newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            await writer.writerow([seed_domain, purl])
                collected.extend((seed_domain, purl) for purl in product_urls)
            finally:
                if frontier.is_empty():
                    print(f"Html queue length is {self.html_queue.qsize()} for {seed_domain}")
                await self.tracker.done()
                self.html_queue.task_done()

    async def __fetcher_worker(self, frontier: URLFrontier, semaphore: asyncio.Semaphore, seed_domain: str):
        print(f"Fetcher worker started for domain {seed_domain}")
        fetcher = AsyncFetcher()
        while True:
            try:
                url, depth = await frontier.next_url()
            except StopAsyncIteration:
                print(f"StopAsyncIteration raised for {seed_domain}, stopping fetcher worker...")
                break
            parsed = urlparse(url)
            if parsed.netloc != seed_domain:
                await self.tracker.done()
                continue
            async with semaphore:
                result = await fetcher.smart_fetch_html(url)
            if result["html"] and result["status"] == 200:
                print(f"Fetched HTML for {url} at depth {depth}")
                await self.html_queue.put((result["url"], result["html"], depth))
                await self.tracker.add()
            else:
                self.logger.info("Failed to fetch HTML for : %s", url)
            await self.tracker.done()

    async def __crawl_and_collect(self, seed_url: str, max_depth: int = 3) -> list[tuple[str, str]]:
        seed_domain = urlparse(seed_url).netloc
        # Create async resources inside the event loop
        if self.logger is None:
            self.logger = setup_logger()
        if self.tracker is None:
            self.tracker = WorkTracker()
        if self.outputLock is None:
            self.outputLock = Lock()

        print(f"seed domain : {seed_domain}")
        frontier = URLFrontier(seed_url=seed_url, max_depth=max_depth, tracker=self.tracker)
        await frontier.add_urls({seed_url}, current_depth=-1)
        collected = []
        semaphore = asyncio.Semaphore(self.CONCURRENT_FETCHERS)
        parser_task = asyncio.create_task(self.__parser_worker(seed_domain, frontier, collected))
        fetcher_tasks = [
            asyncio.create_task(self.__fetcher_worker(frontier, semaphore, seed_domain))
            for _ in range(self.CONCURRENT_FETCHERS)
        ]
        await self.tracker.wait()
        await self.html_queue.put(None)
        print(f"Added None to HTML queue for {seed_domain}, waiting for parser worker to finish...")
        await self.html_queue.join()
        print(f"HTML queue for {seed_domain} is empty, waiting for parser worker to finish...")
        await parser_task
        await frontier.finish()
        print(f"Parser worker for {seed_domain} has finished processing all items.")
        await asyncio.gather(*fetcher_tasks)
        print(f"Fetcher worker for {seed_domain} has finished processing all items.")
        return collected

    async def crawl_multiple_seeds(self, seed_urls: list[str]):
        for seed_url in seed_urls:
            await self.__crawl_and_collect(seed_url)
