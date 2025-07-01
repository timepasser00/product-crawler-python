import asyncio
import csv
from urllib.parse import urlparse
import aiofiles

from async_fetcher import smart_fetch_html
from parser import parse_html
from url_frontier import URLFrontier
from logger_config import setup_logger
from threading import Lock

from work_tracker import WorkTracker

CONCURRENT_FETCHERS = 5
html_queue = asyncio.Queue()
logger = setup_logger()
tracker = WorkTracker()

outputLock = Lock()

async def parser_worker(seed_domain : str, frontier: URLFrontier,
                  collected: list[tuple[str, str]]):
    while True:
        item = await html_queue.get()
        if item is None:
            html_queue.task_done()
            break
        try:
            url, html, depth = item
            child_urls, product_urls = parse_html(url, html, seed_domain)
            print(f"Parsed {len(child_urls)} child URLs and {len(product_urls)} product URLs from {url}")
            await frontier.add_urls(set(child_urls), current_depth=depth)
            for purl in product_urls:
                with outputLock:
                    async with aiofiles.open("product_urls.csv", mode="a", newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        await writer.writerow([seed_domain, purl])
            collected.extend((seed_domain, purl) for purl in product_urls)
        finally:
            if frontier.is_empty():
                print(f"Html queue length is {html_queue.qsize()} for {seed_domain}")
            await tracker.done()
            html_queue.task_done()



async def fetcher_worker(frontier: URLFrontier, semaphore: asyncio.Semaphore,
                         seed_domain: str):

    print(f"Fetcher worker started for domain {seed_domain}")

    while True:
        try:
            url, depth = await frontier.next_url()
        except StopAsyncIteration:
            print(f"StopAsyncIteration raised for {seed_domain}, stopping fetcher worker...")
            break

        parsed = urlparse(url)
        if parsed.netloc != seed_domain:
            await tracker.done()
            continue

        async with semaphore:
            result = await smart_fetch_html(url)
        if result["html"] and result["status"] == 200:
            print(f"Fetched HTML for {url} at depth {depth}")
            await html_queue.put((result["url"], result["html"], depth))
            await tracker.add()
        else:
            logger.info("Failed to fetch HTML for : ", url)
        
        await tracker.done()




async def crawl_and_collect(seed_url: str, max_depth: int =3) -> list[tuple[str, str]]:
    seed_domain = urlparse(seed_url).netloc

    print(f"seed domain : {seed_domain}")

    frontier = URLFrontier(seed_url=seed_url, max_depth=max_depth, tracker=tracker)
    await frontier.add_urls({seed_url}, current_depth=-1)

    collected = []
    semaphore = asyncio.Semaphore(CONCURRENT_FETCHERS)

    parser_tasks = asyncio.create_task(parser_worker(seed_domain, frontier, collected))

    fetcher_task = [
        asyncio.create_task(fetcher_worker(frontier, semaphore, seed_domain))
        for _ in range(CONCURRENT_FETCHERS)
    ]

    await tracker.wait()

    await html_queue.put(None)

    print(f"Added None to HTML queue for {seed_domain}, waiting for parser worker to finish...")

    await html_queue.join()

    print(f"HTML queue for {seed_domain} is empty, waiting for parser worker to finish...")

    await asyncio.gather(*parser_tasks)


    await frontier.finish()

    print(f"Parser worker for {seed_domain} has finished processing all items.")
    await asyncio.gather(*fetcher_task)

    print(f"Fetcher worker for {seed_domain} has finished processing all items.")
    
    return collected


async def crawl_multiple_seeds(seed_urls: list[str], output_csv: str):

    with open(output_csv, mode="w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["seed_domain", "product_url"])

    for seed_url in seed_urls:
        await crawl_and_collect(seed_url)
