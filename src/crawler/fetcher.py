"""Async HTTP client for fetching web resources."""

import asyncio
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from ..utils.rate_limiter import RateLimiter
from ..utils.robots_parser import RobotsParser
from ..utils.http_utils import UserAgentRotator, build_headers
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FetchResult:
    """
    Result from fetching a URL.
    
    Attributes:
        url: The URL that was fetched
        status_code: HTTP status code (0 if request failed)
        headers: Response headers
        content: Response body as bytes
        text: Response body as text
        elapsed: Request duration in seconds
        error: Error message if request failed
    """
    
    url: str
    status_code: int
    headers: Dict[str, str]
    content: bytes = b""
    text: str = ""
    elapsed: float = 0.0
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """Check if request was successful."""
        return 200 <= self.status_code < 300 and self.error is None
    
    @property
    def is_redirect(self) -> bool:
        """Check if response is a redirect."""
        return 300 <= self.status_code < 400
    
    @property
    def is_error(self) -> bool:
        """Check if response is an error."""
        return self.status_code >= 400 or self.error is not None


class Fetcher:
    """
    Async HTTP client with connection pooling and rate limiting.
    
    Features:
    - Async HTTP requests with httpx
    - Connection pooling and HTTP/2 support
    - Rate limiting with random delays
    - User-Agent rotation
    - Robots.txt respect
    - Authentication support
    - Redirect following
    - Timeout handling
    """
    
    def __init__(
        self,
        rate_limiter: RateLimiter,
        robots_parser: RobotsParser,
        user_agents: list,
        timeout: int = 10,
        max_redirects: int = 5,
        auth: Optional[tuple] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        custom_cookies: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize HTTP fetcher.
        
        Args:
            rate_limiter: Rate limiter for polite crawling
            robots_parser: Robots.txt parser
            user_agents: List of User-Agent strings to rotate
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
            auth: Tuple of (username, password) for authentication
            custom_headers: Custom headers to include in requests
            custom_cookies: Custom cookies to include in requests
        """
        self.rate_limiter = rate_limiter
        self.robots_parser = robots_parser
        self.user_agent_rotator = UserAgentRotator(user_agents)
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.custom_headers = custom_headers or {}
        self.custom_cookies = custom_cookies or {}
        
        # Create httpx client with connection pooling
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
            http2=False,  # Disabled - requires h2 package
            follow_redirects=True,
            max_redirects=max_redirects,
            verify=True,
            auth=auth,
        )
        
        self._closed = False
    
    async def fetch(self, url: str) -> FetchResult:
        """
        Fetch URL with rate limiting and error handling.
        
        Args:
            url: URL to fetch
        
        Returns:
            FetchResult with response data or error information
        
        Example:
            >>> fetcher = Fetcher(rate_limiter, robots_parser, user_agents)
            >>> result = await fetcher.fetch("https://example.com")
            >>> if result.is_success:
            ...     print(f"Fetched {len(result.content)} bytes")
        """
        if self._closed:
            return FetchResult(
                url=url,
                status_code=0,
                headers={},
                error="Fetcher is closed"
            )
        
        # Check robots.txt
        user_agent = self.user_agent_rotator.get_next()
        if not await self.robots_parser.can_fetch(url, user_agent):
            logger.debug(f"URL disallowed by robots.txt: {url}")
            return FetchResult(
                url=url,
                status_code=0,
                headers={},
                error="Disallowed by robots.txt"
            )
        
        # Apply rate limiting
        await self.rate_limiter.wait()
        
        # Build headers
        headers = build_headers(user_agent, self.custom_headers)
        
        # Fetch URL
        try:
            import time
            start_time = time.time()
            
            response = await self.client.get(
                url,
                headers=headers,
                cookies=self.custom_cookies,
            )
            
            elapsed = time.time() - start_time
            
            logger.debug(f"Fetched {url} - Status: {response.status_code} - Time: {elapsed:.2f}s")
            
            return FetchResult(
                url=str(response.url),  # Final URL after redirects
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                text=response.text,
                elapsed=elapsed,
            )
        
        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching {url}")
            return FetchResult(
                url=url,
                status_code=0,
                headers={},
                error="Timeout"
            )
        
        except httpx.NetworkError as e:
            logger.warning(f"Network error fetching {url}: {e}")
            return FetchResult(
                url=url,
                status_code=0,
                headers={},
                error=f"Network error: {str(e)}"
            )
        
        except httpx.TooManyRedirects:
            logger.warning(f"Too many redirects for {url}")
            return FetchResult(
                url=url,
                status_code=0,
                headers={},
                error="Too many redirects"
            )
        
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return FetchResult(
                url=url,
                status_code=0,
                headers={},
                error=f"Unexpected error: {str(e)}"
            )
    
    async def close(self) -> None:
        """Close HTTP client and connections."""
        if not self._closed:
            await self.client.aclose()
            self._closed = True
            logger.debug("Fetcher closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
