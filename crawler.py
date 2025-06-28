import asyncio
import csv
import queue
import threading
from urllib.parse import urljoin, urlparse
import aiofiles

from bs4 import BeautifulSoup
from async_fetcher import smart_fetch_html
from parser import parse_html
from url_frontier import URLFrontier
from logger_config import setup_logger
import re
from product_url_analyser import is_dead_end_url
from threading import Lock
from playwright.async_api import async_playwright
from puppeteer_fetcher import fetch_html_with_puppeteer

NUM_PARSER_THREADS = 1
CONCURRENT_FETCHERS = 1
html_queue = asyncio.Queue()
logger = setup_logger()

outputLock = Lock()

async def fetch_with_browser(url: str, base_url: str = "") -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, timeout=15000, wait_until='networkidle')
            html = await page.content()
        except Exception as e:
            html = ""
        await browser.close()

        return {
            "html": html,
            "status": 200 if html else None,
            "url": url
        }


async def parser_worker(seed_domain : str, frontier: URLFrontier,
                  collected: list[tuple[str, str]]):
    print(f"Parser worker started for domain {seed_domain}")
    while True:
        if html_queue.empty():
            print("No more HTML to parse")
        item = await html_queue.get()
        if item is None:
            break 
        try:
            url, html, depth = item
            print(f"Parsing {url} at depth {depth} for the domain {seed_domain}")
            child_urls, product_urls = parse_html(url, html, seed_domain)
            frontier.add_urls(set(child_urls), current_depth=depth)
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
        if not frontier.has_next():
            print("No more url to fetch")
            break

        url, depth = frontier.next_url()
        parsed = urlparse(url)
        # logger.info(f"Fetching {url} with domain {parsed.netloc} at depth {depth} for the domain {seed_domain}")
        
        # Check if the URL belongs to the seed domain
        if parsed.netloc != seed_domain:
            continue

        async with semaphore:
            result = await smart_fetch_html(url)
        if result["html"] and result["status"] == 200:
            html_queue.put((result["url"], result["html"], depth))
        else:
            print("Failed to fetch or parse HTML for : ", url)



async def crawl_and_collect(seed_url: str, max_depth=3) -> list[tuple[str, str]]:
    seed_domain = urlparse(seed_url).netloc

    print(f"seed domain : {seed_domain}")

    frontier = URLFrontier(seed_url=seed_url, max_depth=max_depth)
    frontier.add_urls({seed_url}, current_depth=-1)

    collected = []
    semaphore = asyncio.Semaphore(CONCURRENT_FETCHERS)

    # Start parser threads
    # parser_threads = []
    # for _ in range(NUM_PARSER_THREADS):
    #     t = threading.Thread(target=parser_worker,
    #                          args=(seed_domain, frontier, collected),
    #                          daemon=True)
    #     t.start()
    #     parser_threads.append(t)



    parser_tasks = [
        asyncio.create_task(parser_worker(seed_domain, frontier, collected))
        for _ in range(NUM_PARSER_THREADS)
    ]

    fetcher_task = [
        asyncio.create_task(fetcher_worker(frontier, semaphore, seed_domain))
        for _ in range(CONCURRENT_FETCHERS)
    ]

    # Start async fetchers
    
    await asyncio.gather(*fetcher_task)

    # Wait for remaining HTML to be parsed
    await html_queue.join()

    # Shutdown parser threads

    # await html_queue.put(None)  # Signal parser workers to exit
    await asyncio.gather(*parser_tasks)
    # for _ in parser_threads:
    #     html_queue.put(None)
    # for t in parser_threads:
    #     t.join()

    for _ in range(NUM_PARSER_THREADS):
        await html_queue.put(None)
    await asyncio.gather(*parser_tasks)

    return collected


async def crawl_multiple_seeds(seed_urls: list[str], output_csv: str):
    all_results = []

    with open(output_csv, mode="w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["seed_domain", "product_url"])

    for seed_url in seed_urls:
        # result = await crawl_and_collect(seed_url)
        # all_results.extend(result)
        await crawl_and_collect(seed_url)
        print("Crawingl completed for seed URL:", seed_url)
    # print(f"Exported {len(all_results)} product URLs to {output_csv}")
