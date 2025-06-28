import re
import urllib.parse
from typing import List, Set, Dict, Optional

class ProductURLAnalyzer:
    """
    Comprehensive product URL analyzer for e-commerce crawling.
    Supports major platforms and provides extensive URL classification.
    """
    
    def __init__(self):
        # Major e-commerce platforms and their product URL patterns
        self.platform_product_patterns = {
            'amazon': [
                r'/dp/[A-Z0-9]{10}',
                r'/gp/product/[A-Z0-9]{10}',
                r'/exec/obidos/ASIN/[A-Z0-9]{10}',
                r'/product-reviews/[A-Z0-9]{10}',
                r'/[^/]+/dp/[A-Z0-9]{10}'
            ],
            'ebay': [
                r'/itm/[0-9]+',
                r'/p/[0-9]+',
                r'/i/[0-9]+',
                r'/deals/[^/]+/[0-9]+'
            ],
            'walmart': [
                r'/ip/[^/]+/[0-9]+',
                r'/product/[^/]+/[0-9]+',
                r'/grocery/ip/[^/]+/[0-9]+'
            ],
            'target': [
                r'/p/[^/]+/-/A-[0-9]+',
                r'/product/[^/]+/-/A-[0-9]+'
            ],
            'etsy': [
                r'/listing/[0-9]+',
                r'/[^/]+/listing/[0-9]+'
            ],
            'shopify': [
                r'/products/[^/?]+',
                r'/collections/[^/]+/products/[^/?]+'
            ],
            'aliexpress': [
                r'/item/[0-9]+\.html',
                r'/store/product/[^/]+/[0-9]+\.html'
            ],
            'alibaba': [
                r'/product-detail/[^/]+_[0-9]+\.html',
                r'/p/[^/]+/[0-9]+\.html'
            ]
        }
        
        # Generic product URL patterns
        self.generic_product_patterns = [
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
            r'/checkout/cart/add/uenc/[^/]+/product/[0-9]+',
            r'/[^/]+\.html\?.*product.*id=\d+',
            r'/product_info\.php\?products_id=\d+',
            r'\.html$',  # Many product pages end with .html
            r'/[^/]*[0-9]{6,}[^/]*$',  # Long numeric IDs often indicate products
        ]
        
        # Dead-end URL patterns that will never lead to products
        self.dead_end_patterns = {
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
                r'/download', r'/subscribe', r'/unsubscribe'
            ]
        }
        
        # Parameters that often indicate non-product pages
        self.dead_end_params = [
            'utm_', 'gclid', 'fbclid', 'ref', 'campaign', 'source',
            'sort', 'filter', 'page', 'limit', 'offset', 'view',
            'search', 'q', 'query', 'keyword'
        ]
        
        # Product-indicating keywords in URLs
        self.product_keywords = [
            'product', 'item', 'goods', 'merchandise', 'article',
            'catalog', 'inventory', 'stock', 'sku', 'model',
            'buy', 'shop', 'store', 'purchase', 'order'
        ]
        
        # Category/listing indicators (usually not product pages)
        self.category_keywords = [
            'category', 'categories', 'collection', 'collections',
            'department', 'section', 'brand', 'brands', 'sale',
            'deals', 'offers', 'clearance', 'outlet'
        ]

    def is_product_url(self, url: str) -> bool:
        """
        Comprehensive method to determine if a URL is a product URL.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            bool: True if the URL is likely a product URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
            
        # Normalize URL
        url = url.lower().strip()
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        path = parsed_url.path
        query = parsed_url.query
        
        # Check if it's a dead-end URL first (higher priority)
        if self.is_dead_end_url(url):
            return False
        
        # Platform-specific product pattern matching
        for platform, patterns in self.platform_product_patterns.items():
            if platform in domain:
                for pattern in patterns:
                    if re.search(pattern, path):
                        return True
        
        # Generic product pattern matching
        for pattern in self.generic_product_patterns:
            if re.search(pattern, path):
                # Additional validation for generic patterns
                if self._has_product_indicators(url, path, query):
                    return True
        
        # Check for product-specific URL structures
        if self._check_product_url_structure(path, query):
            return True
        
        # Check for numeric IDs that often indicate products
        if self._has_product_numeric_patterns(path):
            return True
        
        # Check for product keywords in URL
        if self._has_product_keywords(url):
            # But not if it also has category keywords without product indicators
            if not (self._has_category_keywords(url) and not self._has_strong_product_indicators(url)):
                return True
        
        return False
    
    def is_dead_end_url(self, url: str) -> bool:
        """
        Comprehensive method to determine if a URL will never lead to a product URL.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            bool: True if the URL is a dead-end that won't lead to products, False otherwise
        """
        if not url or not isinstance(url, str):
            return True
            
        # Normalize URL
        url = url.lower().strip()
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        path = parsed_url.path
        query = parsed_url.query
        fragment = parsed_url.fragment
        
        # Check for file extensions that are never product pages
        if re.search(r'\.(css|js|json|xml|txt|pdf|zip|rar|exe|dmg|pkg)$', path):
            return True
        
        # Check for media files
        if re.search(r'\.(jpg|jpeg|png|gif|svg|ico|webp|mp4|mp3|wav|pdf)$', path):
            return True
        
        # Check dead-end patterns
        for category, patterns in self.dead_end_patterns.items():
            for pattern in patterns:
                if re.search(pattern, path) or re.search(pattern, url):
                    return True
        
        # Check for problematic query parameters
        if query:
            query_params = urllib.parse.parse_qs(query)
            for param in query_params.keys():
                if any(dead_param in param.lower() for dead_param in self.dead_end_params):
                    # Exception: if it also has product-indicating parameters
                    if not self._has_product_query_params(query_params):
                        return True
        
        # Check for fragments that indicate non-product content
        if fragment and re.search(r'(reviews|comments|questions|specs)', fragment):
            return True
        
        # Check for obvious non-e-commerce domains
        non_ecommerce_domains = [
            'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'linkedin.com', 'pinterest.com', 'reddit.com', 'wikipedia.org',
            'github.com', 'stackoverflow.com', 'medium.com', 'blog.',
            'news.', 'forum.', 'community.', 'support.', 'help.'
        ]
        
        for non_ecommerce in non_ecommerce_domains:
            if non_ecommerce in domain:
                return True
        
        # Check for URLs that are clearly navigation/utility pages
        navigation_patterns = [
            r'/home$', r'/index$', r'/$', r'/main$',
            r'/sitemap', r'/robots\.txt', r'/favicon\.ico',
            r'/error', r'/404', r'/500', r'/maintenance'
        ]
        
        for pattern in navigation_patterns:
            if re.search(pattern, path):
                return True
        
        # Check for social media sharing URLs
        if re.search(r'/(share|social|follow)', path):
            return True
        
        # Check for email/newsletter URLs
        if re.search(r'/(email|newsletter|subscribe)', path):
            return True
        
        # Check for download/file URLs
        if re.search(r'/(download|file|attachment|document)', path):
            return True
        
        # Check for URLs with only category indicators and no product indicators
        if (self._has_only_category_keywords(url) and 
            not self._has_product_indicators(url, path, query)):
            return True
        
        return False
    
    def _has_product_indicators(self, url: str, path: str, query: str) -> bool:
        """Check for various product indicators in the URL."""
        # Product-specific parameters
        product_params = ['product_id', 'item_id', 'sku', 'model', 'variant']
        if query:
            for param in product_params:
                if param in query.lower():
                    return True
        
        # Product keywords in path
        for keyword in self.product_keywords:
            if keyword in path:
                return True
        
        return False
    
    def _check_product_url_structure(self, path: str, query: str) -> bool:
        """Check for common product URL structures."""
        # Common e-commerce URL structures
        structures = [
            r'/[^/]+/[^/]+/[0-9]+',  # /category/subcategory/123
            r'/[^/]+-[0-9]+',        # /product-name-123
            r'/[0-9]+-[^/]+',        # /123-product-name
            r'/[^/]+_[0-9]+',        # /product_name_123
        ]
        
        for structure in structures:
            if re.search(structure, path):
                return True
        
        return False
    
    def _has_product_numeric_patterns(self, path: str) -> bool:
        """Check for numeric patterns that often indicate products."""
        # Long numeric sequences often indicate product IDs
        if re.search(r'/[0-9]{6,}', path):
            return True
        
        # Mixed alphanumeric codes
        if re.search(r'/[A-Z0-9]{8,}', path):
            return True
        
        return False
    
    def _has_product_keywords(self, url: str) -> bool:
        """Check if URL contains product-related keywords."""
        for keyword in self.product_keywords:
            if keyword in url.lower():
                return True
        return False
    
    def _has_category_keywords(self, url: str) -> bool:
        """Check if URL contains category-related keywords."""
        for keyword in self.category_keywords:
            if keyword in url.lower():
                return True
        return False
    
    def _has_only_category_keywords(self, url: str) -> bool:
        """Check if URL has only category keywords without product indicators."""
        has_category = self._has_category_keywords(url)
        has_product = self._has_product_keywords(url)
        
        return has_category and not has_product
    
    def _has_strong_product_indicators(self, url: str) -> bool:
        """Check for strong product indicators that override category keywords."""
        strong_indicators = ['product/', 'item/', '/p/', 'sku', 'model']
        for indicator in strong_indicators:
            if indicator in url.lower():
                return True
        return False
    
    def _has_product_query_params(self, query_params: Dict) -> bool:
        """Check if query parameters indicate a product page."""
        product_query_indicators = ['product_id', 'item_id', 'sku', 'pid', 'id']
        for param in query_params.keys():
            if any(indicator in param.lower() for indicator in product_query_indicators):
                return True
        return False


# Convenience functions for easy importing
def is_product_url(url: str) -> bool:
    """
    Convenience function to check if a URL is a product URL.
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        bool: True if the URL is likely a product URL, False otherwise
    """
    analyzer = ProductURLAnalyzer()
    return analyzer.is_product_url(url)

def is_dead_end_url(url: str) -> bool:
    """
    Convenience function to check if a URL is a dead-end.
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        bool: True if the URL is a dead-end that won't lead to products, False otherwise
    """
    analyzer = ProductURLAnalyzer()
    return analyzer.is_dead_end_url(url)
