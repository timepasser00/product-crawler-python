import asyncio
from crawler import crawl_multiple_seeds

if __name__ == "__main__":
    seed_urls = [
        "https://www.virgio.com/",
        "https://www.tatacliq.com/",
        "https://www.nykaafashion.com/",
        "https://www.westside.com/"
    ]

    output_csv = "product_urls.csv"

    asyncio.run(crawl_multiple_seeds(seed_urls, output_csv))
    