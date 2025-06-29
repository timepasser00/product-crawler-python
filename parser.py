from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple
from product_page_classifier import ProductPageClassifier
from product_url_analyser import is_dead_end_url
from logger_config import setup_logger


logger = setup_logger()
productPageClassifer = ProductPageClassifier()

def parse_html(page_url: str, html: str, seed_domain: str) -> Tuple[List[str], List[str]] :
    soup = BeautifulSoup(html, "lxml")
    child_urls = set()
    product_urls = set()

    result = productPageClassifer.analyze(soup, page_url, None, logger.info)

    if result["is_product_page"]:
        product_urls.add(page_url)

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        url = urljoin(page_url, href)
        parsed = urlparse(url)

        if parsed.netloc != seed_domain:
            continue

        normalized = parsed._replace(fragment="").geturl().rstrip("/")

        if not is_dead_end_url(parsed.path):
            child_urls.add(normalized)

    return child_urls, product_urls

