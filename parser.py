import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple
from product_page_classifier import ProductPageClassifier
from product_url_analyser import is_dead_end_url, is_product_url
from logger_config import setup_logger

# Example product URL pattern heuristic
PRODUCT_PATH_KEYWORDS = ["/product/", "/item/", "/dp/", "/p/", "/sku/", "/gp/product/", "/prd/"]
NON_PRODUCT_HINTS = ["/category", "/brand", "/collections", "/search",
                      "/filter", "/sort", "/cart", "/checkout", "/login", "/pages",
                      "/signup", "/account", "/help", "/terms", "/privacy", "/blog", "/about", "/contact"]
# parser.py or a shared config file
IRRELEVANT_PATHS = [
    "/blog", "/blogs", "/about", "/careers", "/contact",
    "/terms", "/privacy", "/help", "/faq", "/news", "/media",
    "/sitemap", "/press"
]

logger = setup_logger()
productPageClassifer = ProductPageClassifier()

def is_irrelevant_url(path: str) -> bool:
    return any(path.startswith(p) for p in IRRELEVANT_PATHS)


# def is_product_url(url: str) -> bool:
#     parsed = urlparse(url)
#     path = parsed.path.lower()

#     # 1. Must have enough path depth
#     path_parts = [p for p in path.split("/") if p]
#     if len(path_parts) < 2:
#         return False

#     # 2. Skip known non-product paths
#     if any(skip in path for skip in NON_PRODUCT_HINTS):
#         return False

#     # 3. Check if path contains any product-indicative keywords
#     if any(keyword in path for keyword in PRODUCT_PATH_KEYWORDS):
#         return True

#     # 4. Check if last path segment looks like a slug or ID
#     last_segment = path_parts[-1]
#     if re.fullmatch(r"[a-z0-9\-]{8,}", last_segment):
#         return True

#     return False



# def parse_html(base_url: str, html: str, seed_domain: str) -> Tuple[List[str], List[str]]:
#     soup = BeautifulSoup(html, "html.parser")
#     anchors = soup.find_all("a", href=True)

#     child_urls = set()
#     product_urls = set()

#     for tag in anchors:
#         href = tag.get("href")
#         full_url = urljoin(base_url, href)
#         parsed = urlparse(full_url)

#         # Skip non-http(s)
#         if parsed.scheme not in ("http", "https"):
#             continue

#         if parsed.netloc != seed_domain:
#             continue

#         if is_dead_end_url(parsed.path):
#             logger.debug(f"Skipping dead-end URL: {full_url}")
#             continue

#         # Normalize (remove fragment)
#         full_url = full_url.split("#")[0]

#         if is_product_url(full_url):
#             product_urls.add(full_url)
#         else:
#             child_urls.add(full_url)

#     return list(child_urls), list(product_urls)


def looks_like_product_page(soup: BeautifulSoup) -> bool:
    # Count price-like texts
    price_regex = re.compile(r"(₹|\$|€)\s?\d{2,}")
    prices = soup.find_all(string=price_regex)
    price_count = len(prices)

    # Count product-like images
    images = soup.find_all("img")
    image_candidates = [
        img for img in images if any(
            kw in (img.get("alt", "") + img.get("title", "") + img.get("src", "")).lower()
            for kw in ["product", "main", "zoom", "detail"]
        )
    ]

    # Look for CTA buttons (buy/add to cart)
    cta = soup.find(string=re.compile(r"(add to cart|buy now|select size|checkout)", re.IGNORECASE))

    # Look for a prominent product title (usually in h1)
    h1 = soup.find("h1")
    has_title = bool(h1 and len(h1.get_text(strip=True)) >= 10)

    # Related products section at the bottom (optional)
    similar_section = soup.find(string=re.compile(r"(similar|you may also like|customers also bought)", re.IGNORECASE))

    # Heuristic scoring logic
    score = 0

    if price_count in (1, 2):  # not too many
        score += 1
    if len(image_candidates) >= 1:
        score += 1
    if cta:
        score += 1
    if has_title:
        score += 1
    if similar_section:
        score += 0.5

    # Threshold score for classifying as product page
    return score >= 3





def parse_html_for_links(base_url, soup, seed_domain):
    links = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        url = urljoin(base_url, href)
        parsed = urlparse(url)

        if parsed.netloc != seed_domain:
            continue

        normalized = parsed._replace(fragment="").geturl().rstrip("/")
        if not is_dead_end_url(parsed.path):
            links.add(normalized)

    return links, []




def parse_html(page_url: str, html: str, seed_domain: str) -> Tuple[List[str], List[str]] :
    soup = BeautifulSoup(html, "html.parser")
    child_urls = set()
    product_urls = set()

    # 1. Detect if current page is a product page
    # if looks_like_product_page(soup):
    #     product_urls.add(page_url)

    result = productPageClassifer.analyze(soup, page_url, None, logger.info)

    # logger.info(f"Detected page: {page_url} with score {result['score']}, explanation: {result['explanation']}, confidence: {result['confidence']}")
    if result["is_product_page"]:
        product_urls.add(page_url)

    # 2. Extract candidate links to crawl
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        url = urljoin(page_url, href)
        parsed = urlparse(url)

        if parsed.netloc != seed_domain:
            continue

        normalized = parsed._replace(fragment="").geturl().rstrip("/")

        if not is_irrelevant_url(parsed.path):
            child_urls.add(normalized)

    return child_urls, product_urls

