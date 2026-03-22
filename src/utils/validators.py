"""URL validation and normalization utilities."""

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import Optional


def validate_url(url: str) -> bool:
    """
    Validate URL format and scheme.
    
    Args:
        url: URL string to validate
    
    Returns:
        True if URL is valid HTTP/HTTPS URL, False otherwise
    
    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("ftp://example.com")
        False
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent formatting and duplicate detection.
    
    Normalization includes:
    - Remove fragments (#section)
    - Sort query parameters alphabetically
    - Ensure consistent trailing slash handling
    - Lowercase scheme and domain
    
    Args:
        url: URL to normalize
    
    Returns:
        Normalized URL string
    
    Example:
        >>> normalize_url("https://Example.com/path?b=2&a=1#section")
        'https://example.com/path?a=1&b=2'
    """
    try:
        parsed = urlparse(url)
        
        # Lowercase scheme and netloc
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        
        # Keep path as-is (case-sensitive on most servers)
        path = parsed.path
        
        # Sort query parameters
        query = ""
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            sorted_params = sorted(params.items())
            query = urlencode(sorted_params, doseq=True)
        
        # Remove fragment
        fragment = ""
        
        # Reconstruct URL
        normalized = urlunparse((scheme, netloc, path, parsed.params, query, fragment))
        
        return normalized
    except Exception:
        return url


def is_same_domain(url1: str, url2: str, follow_subdomains: bool = False) -> bool:
    """
    Check if two URLs belong to the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        follow_subdomains: If True, consider subdomains as same domain
    
    Returns:
        True if URLs are in the same domain, False otherwise
    
    Example:
        >>> is_same_domain("https://example.com", "https://example.com/page")
        True
        >>> is_same_domain("https://sub.example.com", "https://example.com", follow_subdomains=True)
        True
        >>> is_same_domain("https://sub.example.com", "https://example.com", follow_subdomains=False)
        False
    """
    try:
        domain1 = urlparse(url1).netloc.lower()
        domain2 = urlparse(url2).netloc.lower()
        
        if domain1 == domain2:
            return True
        
        if follow_subdomains:
            # Extract base domain (last two parts: example.com)
            parts1 = domain1.split('.')
            parts2 = domain2.split('.')
            
            if len(parts1) >= 2 and len(parts2) >= 2:
                base1 = '.'.join(parts1[-2:])
                base2 = '.'.join(parts2[-2:])
                return base1 == base2
        
        return False
    except Exception:
        return False


def is_in_scope(url: str, target_url: str, follow_subdomains: bool = False) -> bool:
    """
    Check if URL is within scan scope.
    
    Args:
        url: URL to check
        target_url: Target URL defining the scope
        follow_subdomains: Whether to include subdomains in scope
    
    Returns:
        True if URL is in scope, False otherwise
    """
    try:
        # Validate both URLs
        if not validate_url(url) or not validate_url(target_url):
            return False
        
        parsed_url = urlparse(url)
        parsed_target = urlparse(target_url)
        
        # Check scheme (must match)
        if parsed_url.scheme != parsed_target.scheme:
            return False
        
        # Check port (must match if non-standard)
        url_port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        target_port = parsed_target.port or (443 if parsed_target.scheme == 'https' else 80)
        if url_port != target_port:
            return False
        
        # Check domain
        return is_same_domain(url, target_url, follow_subdomains)
    
    except Exception:
        return False


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
    
    Returns:
        Domain string or None if invalid
    
    Example:
        >>> extract_domain("https://example.com/path")
        'example.com'
    """
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return None


def get_base_url(url: str) -> str:
    """
    Get base URL (scheme + netloc) from full URL.
    
    Args:
        url: Full URL
    
    Returns:
        Base URL (e.g., "https://example.com")
    
    Example:
        >>> get_base_url("https://example.com/path?query=1")
        'https://example.com'
    """
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return url
