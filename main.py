import asyncio
from crawler import AsyncCrawler

if __name__ == "__main__":
    seed_urls = [
        "https://www.virgio.com/",
        "https://www.tatacliq.com/",
        "https://nykaafashion.com/",
        "https://www.westside.com/"
    ]

    crawler = AsyncCrawler(output_csv="product_urls.csv")
    asyncio.run(crawler.crawl_multiple_seeds(seed_urls))
    