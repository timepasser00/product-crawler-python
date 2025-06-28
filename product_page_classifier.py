import re
import math
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from config import DEFAULT_FEATURE_WEIGHTS

class ProductPageClassifier:
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    @staticmethod
    def analyze(soup: BeautifulSoup, url: str = "", weights: dict = None, logger=print):
        weights = weights or DEFAULT_FEATURE_WEIGHTS
        score = 0.0
        explanation = []

        for script in soup(["script", "style"]):
            script.decompose()

        def log(msg):
            msg = msg + "\n"
            explanation.append(msg)

        # Positive indicators
        price_texts = soup.find_all(string=re.compile(r'(₹|\$|€)\s?\d{2,}'))
        if price_texts:
            score += weights["price_present"]
            log(f"+{weights['price_present']}: Price found '{price_texts[0].strip()}'")
        else:
            score += weights["no_price_at_all"]
            log(f"{weights['no_price_at_all']}: No price detected")

        img_tags = soup.find_all("img")
        main_imgs = [img for img in img_tags if any(
            kw in (img.get("alt", "") + img.get("src", "")).lower()
            for kw in ["product", "zoom", "main"]
        )]
        if len(main_imgs) >= 1:
            score += weights["single_main_image"]
            log(f"+{weights['single_main_image']}: Product-like image detected")
        if len(img_tags) > 10:
            score += weights["too_many_images"]
            log(f"{weights['too_many_images']}: Too many images ({len(img_tags)})")

        if soup.find(string=re.compile(r"add to cart|buy now|select size", re.IGNORECASE)):
            score += weights["add_to_cart_cta"]
            log(f"+{weights['add_to_cart_cta']}: CTA text found")

        h1 = soup.find("h1")
        if h1 and len(h1.get_text(strip=True)) >= 10:
            score += weights["product_title"]
            log(f"+{weights['product_title']}: H1 title found '{h1.get_text(strip=True)}'")

        if soup.find(string=re.compile(r"product details|specifications", re.IGNORECASE)):
            score += weights["spec_section"]
            log(f"+{weights['spec_section']}: Product details section found")

        if soup.find(attrs={"itemtype": re.compile(r"Product", re.IGNORECASE)}):
            score += weights["semantic_schema"]
            log(f"+{weights['semantic_schema']}: Schema.org Product type found")

        if soup.find(string=re.compile(r"similar products|you may also like|recommended", re.IGNORECASE)):
            score += weights["related_products"]
            log(f"+{weights['related_products']}: Related products section found")

        # Negative indicators
        if len(price_texts) > 5:
            score += weights["too_many_prices"]
            log(f"{weights['too_many_prices']}: Too many price tags ({len(price_texts)})")

        if len(soup.find_all("a")) > 10:
            score += weights["many_links"]
            log(f"{weights['many_links']}: Too many links on page")

        if url:
            parsed = urlparse(url)
            if parsed.path.endswith(('/category', '/search', '/blog')):
                score += weights["bad_url_path"]
                log(f"{weights['bad_url_path']}: URL path suggests non-product page")

        if not soup.find("input") and not soup.find("form"):
            score += weights["no_inputs_or_forms"]
            log(f"{weights['no_inputs_or_forms']}: No form or input fields found")

        confidence = ProductPageClassifier.sigmoid(score)
        is_product_page = confidence >= 0.8

        logger(f"""
        Url: {url}
        Final score: {score}
        Confidence: {confidence:.4f}
        Is product page: {is_product_page}
        """)
        logger("Explanation:\n" + ",".join(explanation))

        return {
            "is_product_page": is_product_page,
            "confidence": round(confidence, 4),
            "score": round(score, 2),
            "explanation": explanation
        }
    