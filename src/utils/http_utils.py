"""HTTP utility functions and helpers."""

import random
from typing import Dict, List


class UserAgentRotator:
    """
    Rotates through a list of User-Agent strings.
    
    Provides round-robin rotation of User-Agent strings to avoid
    detection and blocking by target servers.
    """
    
    def __init__(self, user_agents: List[str]):
        """
        Initialize User-Agent rotator.
        
        Args:
            user_agents: List of User-Agent strings to rotate through
        
        Raises:
            ValueError: If user_agents list is empty
        """
        if not user_agents:
            raise ValueError("user_agents list cannot be empty")
        
        self.user_agents = user_agents
        self.current_index = 0
    
    def get_next(self) -> str:
        """
        Get next User-Agent string in rotation.
        
        Returns:
            User-Agent string
        """
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent
    
    def get_random(self) -> str:
        """
        Get random User-Agent string.
        
        Returns:
            Random User-Agent string from the list
        """
        return random.choice(self.user_agents)


def build_headers(
    user_agent: str,
    custom_headers: Dict[str, str] = None,
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    accept_language: str = "en-US,en;q=0.9",
    accept_encoding: str = "gzip, deflate, br"
) -> Dict[str, str]:
    """
    Build HTTP headers for requests.
    
    Args:
        user_agent: User-Agent string
        custom_headers: Additional custom headers to include
        accept: Accept header value
        accept_language: Accept-Language header value
        accept_encoding: Accept-Encoding header value
    
    Returns:
        Dictionary of HTTP headers
    
    Example:
        >>> headers = build_headers("MyBot/1.0", {"X-Custom": "value"})
        >>> print(headers['User-Agent'])
        'MyBot/1.0'
    """
    headers = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Language': accept_language,
        'Accept-Encoding': accept_encoding,
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Add custom headers (overrides defaults if same key)
    if custom_headers:
        headers.update(custom_headers)
    
    return headers


def parse_content_type(content_type: str) -> tuple:
    """
    Parse Content-Type header.
    
    Args:
        content_type: Content-Type header value
    
    Returns:
        Tuple of (media_type, charset)
    
    Example:
        >>> media_type, charset = parse_content_type("text/html; charset=utf-8")
        >>> print(media_type)
        'text/html'
        >>> print(charset)
        'utf-8'
    """
    if not content_type:
        return ('text/html', 'utf-8')
    
    parts = content_type.split(';')
    media_type = parts[0].strip().lower()
    
    charset = 'utf-8'
    for part in parts[1:]:
        if 'charset=' in part:
            charset = part.split('=')[1].strip().strip('"\'')
            break
    
    return (media_type, charset)


def is_html_content(content_type: str) -> bool:
    """
    Check if Content-Type indicates HTML content.
    
    Args:
        content_type: Content-Type header value
    
    Returns:
        True if content is HTML, False otherwise
    
    Example:
        >>> is_html_content("text/html; charset=utf-8")
        True
        >>> is_html_content("application/json")
        False
    """
    if not content_type:
        return False
    
    media_type, _ = parse_content_type(content_type)
    return media_type in ['text/html', 'application/xhtml+xml']


def format_size(size_bytes: int) -> str:
    """
    Format byte size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string (e.g., "1.5 KB", "2.3 MB")
    
    Example:
        >>> format_size(1536)
        '1.5 KB'
        >>> format_size(2500000)
        '2.4 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sanitize_header_value(value: str) -> str:
    """
    Sanitize header value by removing control characters.
    
    Args:
        value: Header value to sanitize
    
    Returns:
        Sanitized header value
    """
    # Remove control characters and newlines
    return ''.join(char for char in value if ord(char) >= 32 and char not in ['\r', '\n'])
