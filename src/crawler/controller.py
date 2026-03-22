"""Crawler controller for orchestrating web page discovery."""

import asyncio
from typing import Set

from .fetcher import Fetcher
from .parser import Parser
from .frontier import Frontier
from ..utils.validators import is_in_scope
from ..utils.http_utils import is_html_content
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CrawlerController:
    """
    Orchestrates the crawling process using async/await patterns.
    
    Coordinates the Fetcher, Parser, and Frontier components to discover
    and navigate web pages. Enforces crawl depth limits and scope restrictions.
    
    Attributes:
        fetcher: HTTP fetcher for retrieving pages
        parser: HTML parser for extracting links
        frontier: URL queue manager
        target_url: Starting URL defining the scope
        max_depth: Maximum crawl depth
        follow_subdomains: Whether to follow subdomain links
        concurrency: Maximum concurrent requests
    """
    
    def __init__(
        self,
        fetcher: Fetcher,
        parser: Parser,
        frontier: Frontier,
        target_url: str,
        max_depth: int = 2,
        follow_subdomains: bool = False,
        concurrency: int = 10,
    ):
        """
        Initialize crawler controller.
        
        Args:
            fetcher: HTTP fetcher instance
            parser: HTML parser instance
            frontier: URL frontier instance
            target_url: Starting URL for the crawl
            max_depth: Maximum crawl depth from starting URL
            follow_subdomains: Whether to crawl subdomains
            concurrency: Maximum number of concurrent requests
        """
        self.fetcher = fetcher
        self.parser = parser
        self.frontier = frontier
        self.target_url = target_url
        self.max_depth = max_depth
        self.follow_subdomains = follow_subdomains
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)
        
        # Statistics
        self.pages_crawled = 0
        self.errors = []
    
    async def crawl(self, start_url: str) -> Set[str]:
        """
        Main crawl loop - returns all discovered URLs.
        
        Args:
            start_url: URL to start crawling from
        
        Returns:
            Set of all discovered URLs
        
        Example:
            >>> controller = CrawlerController(fetcher, parser, frontier, "https://example.com")
            >>> urls = await controller.crawl("https://example.com")
            >>> print(f"Discovered {len(urls)} URLs")
        """
        logger.info(f"Starting crawl from {start_url} (max_depth={self.max_depth})")
        
        # Add starting URL to frontier
        self.frontier.add_url(start_url, depth=0)
        
        # Process URLs in batches
        while self.frontier.has_pending():
            # Get batch of URLs
            batch = []
            for _ in range(self.concurrency):
                if not self.frontier.has_pending():
                    break
                
                url_depth = self.frontier.get_next()
                if url_depth:
                    url, depth = url_depth
                    if depth <= self.max_depth:
                        batch.append((url, depth))
            
            if not batch:
                break
            
            # Process batch concurrently
            tasks = [self._process_url(url, depth) for url, depth in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Add discovered URLs to frontier
            for result in results:
                if isinstance(result, set):
                    for url in result:
                        # Get depth from batch
                        parent_depth = next((d for u, d in batch if u in str(result)), 0)
                        self.frontier.add_url(url, depth=parent_depth + 1)
                elif isinstance(result, Exception):
                    logger.error(f"Error in crawl batch: {result}")
                    self.errors.append(str(result))
        
        # Get statistics
        stats = self.frontier.get_stats()
        logger.info(
            f"Crawl complete: {stats.discovered} URLs discovered, "
            f"{stats.visited} visited, {len(self.errors)} errors"
        )
        
        return self.frontier.get_all_discovered()
    
    async def _process_url(self, url: str, depth: int) -> Set[str]:
        """
        Fetch, parse, and extract links from a single URL.
        
        Args:
            url: URL to process
            depth: Current crawl depth
        
        Returns:
            Set of discovered URLs
        """
        async with self.semaphore:
            # Check if already visited
            if self.frontier.is_visited(url):
                return set()
            
            # Mark as visited
            self.frontier.mark_visited(url)
            
            # Fetch URL
            result = await self.fetcher.fetch(url)
            
            if result.is_error:
                logger.debug(f"Error fetching {url}: {result.error}")
                self.errors.append(f"{url}: {result.error}")
                return set()
            
            self.pages_crawled += 1
            logger.debug(f"Crawled {url} (depth={depth}, status={result.status_code})")
            
            # Only parse HTML content
            content_type = result.headers.get('content-type', '')
            if not is_html_content(content_type):
                logger.debug(f"Skipping non-HTML content: {url} ({content_type})")
                return set()
            
            # Parse and extract links
            try:
                links = self.parser.parse_links(result.text, url)
                
                # Filter links by scope
                in_scope_links = {
                    link for link in links
                    if self._is_in_scope(link)
                }
                
                logger.debug(
                    f"Extracted {len(links)} links from {url}, "
                    f"{len(in_scope_links)} in scope"
                )
                
                return in_scope_links
            
            except Exception as e:
                logger.error(f"Error parsing {url}: {e}")
                self.errors.append(f"{url}: Parse error - {str(e)}")
                return set()
    
    def _is_in_scope(self, url: str) -> bool:
        """
        Check if URL is within scan scope.
        
        Args:
            url: URL to check
        
        Returns:
            True if URL is in scope, False otherwise
        """
        return is_in_scope(url, self.target_url, self.follow_subdomains)
    
    def get_stats(self) -> dict:
        """
        Get crawl statistics.
        
        Returns:
            Dictionary with crawl statistics
        """
        frontier_stats = self.frontier.get_stats()
        return {
            'pages_crawled': self.pages_crawled,
            'urls_discovered': frontier_stats.discovered,
            'urls_visited': frontier_stats.visited,
            'urls_pending': frontier_stats.pending,
            'errors': len(self.errors),
        }
