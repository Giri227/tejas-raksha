"""URL queue management with duplicate detection."""

from collections import deque
from dataclasses import dataclass
from typing import Optional, Set, Tuple


@dataclass
class FrontierStats:
    """
    Statistics about the URL frontier.
    
    Attributes:
        discovered: Total number of unique URLs discovered
        visited: Number of URLs that have been visited
        pending: Number of URLs waiting to be visited
    """
    
    discovered: int
    visited: int
    pending: int


class Frontier:
    """
    URL queue management system with duplicate detection.
    
    Manages the queue of URLs to visit and tracks which URLs have already
    been visited to prevent duplicates. Uses efficient data structures
    (deque for queue, set for visited tracking).
    
    Attributes:
        queue: Queue of (url, depth) tuples to visit
        visited: Set of URLs that have been visited
        discovered: Set of all URLs discovered
    """
    
    def __init__(self):
        """Initialize frontier with empty queue and visited set."""
        self.queue: deque = deque()
        self.visited: Set[str] = set()
        self.discovered: Set[str] = set()
    
    def add_url(self, url: str, depth: int) -> bool:
        """
        Add URL to queue if not already visited.
        
        Args:
            url: URL to add
            depth: Crawl depth of this URL
        
        Returns:
            True if URL was added, False if already visited
        
        Example:
            >>> frontier = Frontier()
            >>> frontier.add_url("https://example.com", 0)
            True
            >>> frontier.add_url("https://example.com", 0)  # Duplicate
            False
        """
        # Add to discovered set
        self.discovered.add(url)
        
        # Check if already visited
        if url in self.visited:
            return False
        
        # Check if already in queue
        # Note: This is O(n) but queue should be relatively small
        for queued_url, _ in self.queue:
            if queued_url == url:
                return False
        
        # Add to queue
        self.queue.append((url, depth))
        return True
    
    def get_next(self) -> Optional[Tuple[str, int]]:
        """
        Get next URL and depth from queue.
        
        Returns:
            Tuple of (url, depth) or None if queue is empty
        
        Example:
            >>> frontier = Frontier()
            >>> frontier.add_url("https://example.com", 0)
            >>> url, depth = frontier.get_next()
            >>> print(url, depth)
            https://example.com 0
        """
        if not self.queue:
            return None
        
        return self.queue.popleft()
    
    def mark_visited(self, url: str) -> None:
        """
        Mark URL as visited.
        
        Args:
            url: URL to mark as visited
        
        Example:
            >>> frontier = Frontier()
            >>> frontier.mark_visited("https://example.com")
            >>> frontier.is_visited("https://example.com")
            True
        """
        self.visited.add(url)
    
    def is_visited(self, url: str) -> bool:
        """
        Check if URL has been visited.
        
        Args:
            url: URL to check
        
        Returns:
            True if URL has been visited, False otherwise
        """
        return url in self.visited
    
    def has_pending(self) -> bool:
        """
        Check if queue has URLs to process.
        
        Returns:
            True if queue is not empty, False otherwise
        """
        return len(self.queue) > 0
    
    def get_stats(self) -> FrontierStats:
        """
        Get frontier statistics.
        
        Returns:
            FrontierStats with discovered, visited, and pending counts
        """
        return FrontierStats(
            discovered=len(self.discovered),
            visited=len(self.visited),
            pending=len(self.queue)
        )
    
    def get_all_discovered(self) -> Set[str]:
        """
        Get set of all discovered URLs.
        
        Returns:
            Set of all URLs that have been discovered
        """
        return self.discovered.copy()
    
    def clear(self) -> None:
        """Clear all frontier data."""
        self.queue.clear()
        self.visited.clear()
        self.discovered.clear()
    
    def __len__(self) -> int:
        """Return number of pending URLs in queue."""
        return len(self.queue)
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"Frontier(discovered={stats.discovered}, "
            f"visited={stats.visited}, pending={stats.pending})"
        )
