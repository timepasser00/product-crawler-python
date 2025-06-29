import re
import urllib.parse
from typing import List, Set, Dict, Optional
from feature_weights import DEFAULL_PRODUCT_URL_WEIGHTS
from product_patterns import DEAD_END_PATTERNS, PRODUCT_URL_PATTERNS

class ProductURLAnalyzer:
    """
    Comprehensive product URL analyzer for e-commerce crawling.
    Supports major platforms and provides extensive URL classification.
    """

    def is_product_url(self, url: str, weights: dict = None):
        """
        Comprehensive method to determine if a URL is a product URL.
        
        Args:
            url (str): The URL to analyze
            weights (dict, optional): Weights for scoring different URL patterns.
                                       Defaults to DEFAULL_PRODUCT_URL_WEIGHTS.
        Returns:
            bool: True if the URL is likely a product URL, False otherwise
        """

        score = 0.0
        explanation = []
        weights = weights or DEFAULL_PRODUCT_URL_WEIGHTS


        if not url or not isinstance(url, str):
            score = weights.get('invalid_url', 0)
            explanation.append(f"{weights['invalid_url']} : Invalid Url {score}")
            return False
            
        url = url.lower().strip()
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        path = parsed_url.path
        query = parsed_url.query
        score = 0
        explanation = []
        
        # Check if it's a dead-end URL first (higher priority)
        if self.is_dead_end_url(url):
            score = weights.get('dead_end_url', 0) 
            explanation.append(f"{weights['dead_end_url']} : Dead-end URL {score}")
            return False , score, explanation
        
        # Check for product URL patterns
        for pattern in PRODUCT_URL_PATTERNS:
            if re.search(pattern, path):
                score += weights.get('product_pattern', 1)
                explanation.append(f"{weights['product_pattern']} : Product pattern matched {pattern} {score}")
                return True, score, explanation
        
        return False, score, explanation
    
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
        for category, patterns in DEAD_END_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, path) or re.search(pattern, url):
                    return True
        
        if re.search(r'/(share|social|follow)', path):
            return True
        
        # Check for email/newsletter URLs
        if re.search(r'/(email|newsletter|subscribe)', path):
            return True
        
        # Check for download/file URLs
        if re.search(r'/(download|file|attachment|document)', path):
            return True
        
        return False
    
    
# Convenience functions for easy importing
def is_product_url(url: str):
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
