DEFAULT_FEATURE_WEIGHTS = {
    # Positive indicators
    "price_present": 1.0,
    "spec_section": 1.0,
    "semantic_schema": 1.0,
    "related_products": 1.0,
    'exact_one_cta': 2.0,

    # Negative indicators
    "many_links": -1.0,
    "bad_url_path": -1.0,
    "too_many_images": -1.0,
    "no_inputs_or_forms": -1.0,
    "no_price_at_all": -1.0,
    "multiple_cta": -1.0,
}

DEFAULL_PRODUCT_URL_WEIGHTS = {

    "is_dead_end": -2.0,
    "invalid_url": -3.0,
    "product_pattern": 1.0,
}

IRRELEVANT_PATHS = [
    "/blog", "/blogs", "/about", "/careers", "/contact",
    "/terms", "/privacy", "/help", "/faq", "/news", "/media",
    "/sitemap", "/press"
]
