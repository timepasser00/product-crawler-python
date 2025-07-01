import math, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from product_url_analyser import is_product_url
from feature_weights import DEFAULT_FEATURE_WEIGHTS

class ProductPageClassifier:
    """
    Classifies web pages as product pages or not based on various heuristics and URL patterns.
    """
    
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

    def analyze(self, soup: BeautifulSoup, url: str = "", weights: dict = None, logger=print):
        weights = weights or DEFAULT_FEATURE_WEIGHTS
        score = 0.0
        explanation = []

        for script in soup(["script", "style"]):
            script.decompose()

        def log(msg):
            explanation.append(msg + "\n")

        # --- Price Detection ---
        price_texts = soup.find_all(string=re.compile(r'(₹|\$|€)\s?\d{2,}'))
        if price_texts:
            score += weights["price_present"]
            log(f"+{weights['price_present']}: Price found '{price_texts[0].strip()}'")
        else:
            score += weights["no_price_at_all"]
            log(f"{weights['no_price_at_all']}: No price detected")

        # --- CTA Detection ---
        cta_texts = soup.find_all(string=re.compile(r"(add to cart|buy now|select size|select color)", re.IGNORECASE))
        if len(cta_texts) != 1:
            score -= weights["multiple_cta"]
            log(f"-5.0: Buy text is occurence  : ({len(cta_texts)})")
        else:
            score += weights['exact_one_cta'];
            log(f"+{weights['exact_one_cta']}: Exactly one 'Add to Cart' or 'Buy Now' CTA found: {cta_texts[0].strip()}")

        if soup.find(string=re.compile(r"product details|specifications| select size| add to wishlist| know your product", re.IGNORECASE)):
            score += weights["spec_section"]
            log(f"+{weights['spec_section']}: Product details section found")

        # if soup.find(attrs={"itemtype": re.compile(r"Product", re.IGNORECASE)}):
        #     score += weights["semantic_schema"]
        #     log(f"+{weights['semantic_schema']}: Schema.org Product detected")

        if soup.find(string=re.compile(r"similar products|you may also like|recommended", re.IGNORECASE)):
            score += weights["related_products"]
            log(f"+{weights['related_products']}: Related/recommended section found")

        num_links = len(soup.find_all("a"))
        # if num_links > 20:
        #     score += weights["many_links"]
        #     log(f"{weights['many_links']}: Many links ({num_links})")

        if not soup.find("input") and not soup.find("form"):
            score += weights["no_inputs_or_forms"]
            log(f"{weights['no_inputs_or_forms']}: No inputs/forms found")

        # --- URL Analysis ---
        is_prod_url, url_score, url_explanation = is_product_url(url)
        if is_prod_url:
            score += 2.0
        # score += url_score
        explanation.extend(url_explanation)

        confidence = ProductPageClassifier.sigmoid(score)
        is_product_page = confidence >= 0.8

        # Short-circuit if confidence is low
        if not len(cta_texts) == 1 and not price_texts:
            confidence = 0.0
            is_product_page = False
            log("Short-circuited: Lacking all core indicators (CTA, price, image)")

        logger(f"""
        Url: {url}
        Final score: {score}
        Confidence: {confidence:.4f}
        Is product page: {is_product_page}
        """)
        logger("Explanation:\n" + "".join(explanation))

        return {
            "is_product_page": is_product_page,
            "confidence": round(confidence, 4),
            "score": round(score, 2),
            "explanation": explanation
        }
