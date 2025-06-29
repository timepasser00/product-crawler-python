import asyncio
import csv
from urllib.parse import urlparse
import aiofiles

from async_fetcher import smart_fetch_html
from parser import parse_html
from url_frontier import URLFrontier
from logger_config import setup_logger
from threading import Lock

CONCURRENT_FETCHERS = 5
html_queue = asyncio.Queue()
logger = setup_logger()

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

            logger.info(f"Parsed {len(child_urls)} child URLs and {len(product_urls)} product URLs from {url}")
            await frontier.add_urls(set(child_urls), current_depth=depth)
            for purl in product_urls:
                with outputLock:
                    async with aiofiles.open("product_urls.csv", mode="a", newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        await writer.writerow([seed_domain, purl])
            collected.extend((seed_domain, purl) for purl in product_urls)
        finally:
            html_queue.task_done()



async def fetcher_worker(frontier: URLFrontier, semaphore: asyncio.Semaphore,
                         seed_domain: str):

    print(f"Fetcher worker started for domain {seed_domain}")

    while True:
        try:
            url, depth = await frontier.next_url()
        except asyncio.CancelledError:
            break

        parsed = urlparse(url)
        if parsed.netloc != seed_domain:
            continue

        async with semaphore:
            result = await smart_fetch_html(url)
        if result["html"] and result["status"] == 200:
            logger.info(f"Fetched HTML for {url} at depth {depth}")
            await html_queue.put((result["url"], result["html"], depth))
        else:
            logger.info("Failed to fetch HTML for : ", url)



async def crawl_and_collect(seed_url: str, max_depth=3) -> list[tuple[str, str]]:
    seed_domain = urlparse(seed_url).netloc

    print(f"seed domain : {seed_domain}")

    frontier = URLFrontier(seed_url=seed_url, max_depth=max_depth)
    await frontier.add_urls({seed_url}, current_depth=-1)

    collected = []
    semaphore = asyncio.Semaphore(CONCURRENT_FETCHERS)

    parser_tasks = asyncio.create_task(parser_worker(seed_domain, frontier, collected))

    fetcher_task = [
        asyncio.create_task(fetcher_worker(frontier, semaphore, seed_domain))
        for _ in range(CONCURRENT_FETCHERS)
    ]

    # fetching task stopped
    await asyncio.gather(*fetcher_task)

    # existing html parsing done.
    await html_queue.join()

    # send signal to stop parser worker
    await html_queue.put(None)

    # parsing task stopped.
    await asyncio.gather(*parser_tasks)
    
    return collected


async def crawl_multiple_seeds(seed_urls: list[str], output_csv: str):

    with open(output_csv, mode="w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["seed_domain", "product_url"])

    for seed_url in seed_urls:
        await crawl_and_collect(seed_url)
        logger.info("Crawingl completed for seed URL:", seed_url)
