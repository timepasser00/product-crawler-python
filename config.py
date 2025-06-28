PRODUCT_PATTERNS = [
    r"/product/",
    r"/p/",
    r"/item/",
    r"productId=\d+",
    r"pid=\d+",
    r"skuId=\d+",
    r"collections"
]


DEFAULT_FEATURE_WEIGHTS = {
    # Positive indicators
    "price_present": 2.0,
    "single_main_image": 1.0,
    "add_to_cart_cta": 2.0,
    "product_title": 1.0,
    "spec_section": 1.5,
    "semantic_schema": 1.5,
    "related_products": 0.5,

    # Negative indicators
    "too_many_prices": -2.0,
    "many_links": -0.5,
    "bad_url_path": -1.5,
    "too_many_images": -1.0,
    "no_inputs_or_forms": -1.0,
    "no_price_at_all": -2.0,
}