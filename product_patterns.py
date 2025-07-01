DEAD_END_PATTERNS = {
    'account_auth': [
    r'/login', r'/signin', r'/sign-in', r'/register', r'/signup', r'/sign-up',
    r'/account', r'/profile', r'/my-account', r'/user', r'/member',
    r'/checkout', r'/cart', r'/basket', r'/bag', r'/wishlist', r'/favorites',
    r'/logout', r'/signout', r'/sign-out'
    ],
    'legal_info': [
    r'/terms', r'/privacy', r'/policy', r'/legal', r'/disclaimer',
    r'/cookies', r'/gdpr', r'/compliance', r'/terms-of-service',
    r'/privacy-policy', r'/return-policy', r'/shipping-policy'
    ],
    'company_info': [
    r'/about', r'/contact', r'/careers', r'/jobs', r'/investors',
    r'/press', r'/media', r'/news', r'/blog', r'/help', r'/support',
    r'/faq', r'/customer-service', r'/team', r'/company'
    ],
    'api_technical': [
    r'/api/', r'/ajax/', r'/json/', r'/xml/', r'/rss/', r'/feed/',
    r'/webhook', r'/callback', r'/oauth', r'/auth/', r'/token',
    r'\.css', r'\.js', r'\.json', r'\.xml', r'\.txt', r'\.pdf',
    r'\.jpg', r'\.jpeg', r'\.png', r'\.gif', r'\.svg', r'\.ico',
    r'\.woff', r'\.ttf', r'\.eot'
    ],
    'admin_backend': [
    r'/admin', r'/dashboard', r'/cms', r'/wp-admin', r'/backend',
    r'/manage', r'/control-panel', r'/administrator'
    ],
    'search_filter': [
    r'/search', r'/filter', r'/sort', r'/compare', r'/reviews-only',
    r'/questions', r'/q&a', r'/specifications-only'
    ],
    'non_product_actions': [
    r'/add-to-cart', r'/buy-now', r'/quick-view', r'/share',
    r'/email-friend', r'/track-order', r'/order-status',
    r'/download', r'/subscribe', r'/unsubscribe', r'/reviews',
    ]
}

PRODUCT_URL_PATTERNS = [
    r'/dp/[A-Z0-9]{10}',
    r'/gp/product/[A-Z0-9]{10}',
    r'/exec/obidos/ASIN/[A-Z0-9]{10}',
    r'/product-reviews/[A-Z0-9]{10}',
    r'/[^/]+/dp/[A-Z0-9]{10}',
    r'/itm/[0-9]+',
    r'/p/[0-9]+',
    r'/i/[0-9]+',
    r'/deals/[^/]+/[0-9]+',
    r'/ip/[^/]+/[0-9]+',
    r'/product/[^/]+/[0-9]+',
    r'/grocery/ip/[^/]+/[0-9]+',
    r'/p/[^/]+/-/A-[0-9]+',
    r'/product/[^/]+/-/A-[0-9]+',
    r'/listing/[0-9]+',
    r'/[^/]+/listing/[0-9]+',
    r'/products/[^/?]+',
    r'/collections/[^/]+/products/[^/?]+',
    r'/item/[0-9]+\.html',
    r'/store/product/[^/]+/[0-9]+\.html',
    r'/product-detail/[^/]+_[0-9]+\.html',
    r'/p/[^/]+/[0-9]+\.html',

    # Generic patterns
    r'/product[s]?/[^/?]+',
    r'/item[s]?/[^/?]+',
    r'/p/[^/?]+',
    r'/goods/[^/?]+',
    r'/detail/[^/?]+',
    r'/product-[0-9]+',
    r'/item-[0-9]+',
    r'/[^/]+-p[0-9]+',
    r'/sku[/-][0-9A-Za-z]+',
    r'/catalog/product/view/id/[0-9]+',
    r'/[^/]+\.html\?.*product.*id=\d+',
    r'/product_info\.php\?products_id=\d+',
]
