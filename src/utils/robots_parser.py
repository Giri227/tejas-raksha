"""Robots.txt parsing and URL permission checking."""

import asyncio
from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from .logger import get_logger

logger = get_logger(__name__)


class RobotsParser:
    """
    Parser for robots.txt files with caching.
    
    Fetches and parses robots.txt files to determine if URLs are allowed
    to be crawled. Caches parsed rules per domain for efficiency.
    
    Attributes:
        respect_robots: Whether to respect robots.txt directives
        rules_cache: Cache of parsed robots.txt rules by domain
    """
    
    def __init__(self, respect_robots: bool = True):
        """
        Initialize robots.txt parser.
        
        Args:
            respect_robots: If False, all URLs are allowed regardless of robots.txt
        """
        self.respect_robots = respect_robots
        self.rules_cache: Dict[str, Optional[RobotFileParser]] = {}
        self._lock = asyncio.Lock()
    
    async def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if URL is allowed by robots.txt.
        
        Args:
            url: URL to check
            user_agent: User-Agent string to check against
        
        Returns:
            True if URL can be fetched, False otherwise
        
        Example:
            >>> parser = RobotsParser(respect_robots=True)
            >>> allowed = await parser.can_fetch("https://example.com/page", "MyBot")
        """
        # If not respecting robots.txt, allow all URLs
        if not self.respect_robots:
            return True
        
        try:
            domain = urlparse(url).netloc
            
            # Get or fetch robots.txt for this domain
            if domain not in self.rules_cache:
                await self._fetch_robots(domain)
            
            # Check if URL is allowed
            parser = self.rules_cache.get(domain)
            if parser is None:
                # No robots.txt or fetch failed - allow by default
                return True
            
            return parser.can_fetch(user_agent, url)
        
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            # On error, allow by default
            return True
    
    async def _fetch_robots(self, domain: str) -> None:
        """
        Fetch and parse robots.txt for a domain.
        
        Args:
            domain: Domain to fetch robots.txt from
        """
        async with self._lock:
            # Double-check after acquiring lock
            if domain in self.rules_cache:
                return
            
            robots_url = f"https://{domain}/robots.txt"
            
            try:
                # Use RobotFileParser from urllib
                parser = RobotFileParser()
                parser.set_url(robots_url)
                
                # Read robots.txt (this is synchronous in stdlib)
                # In a real async implementation, we'd use httpx here
                # For now, we'll run it in executor to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, parser.read)
                
                self.rules_cache[domain] = parser
                logger.debug(f"Successfully parsed robots.txt for {domain}")
            
            except Exception as e:
                logger.warning(f"Failed to fetch robots.txt for {domain}: {e}")
                # Cache None to indicate fetch was attempted but failed
                self.rules_cache[domain] = None
    
    def clear_cache(self) -> None:
        """Clear the robots.txt cache."""
        self.rules_cache.clear()
    
    def get_cached_domains(self) -> list:
        """
        Get list of domains with cached robots.txt rules.
        
        Returns:
            List of domain strings
        """
        return list(self.rules_cache.keys())
    
    def __repr__(self) -> str:
        return f"RobotsParser(respect_robots={self.respect_robots}, cached_domains={len(self.rules_cache)})"
