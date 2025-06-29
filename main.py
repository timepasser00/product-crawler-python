import asyncio
from crawler import crawl_multiple_seeds

if __name__ == "__main__":
    seed_urls = [
        "https://www.nykaafashion.com/"
    ]

    output_csv = "product_urls.csv"

    asyncio.run(crawl_multiple_seeds(seed_urls, output_csv))
    