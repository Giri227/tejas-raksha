"""Rate limiting for polite crawling."""

import asyncio
import random
import time
from typing import Optional


class RateLimiter:
    """
    Rate limiter with random delays between requests.
    
    Implements polite crawling by introducing configurable random delays
    between HTTP requests to avoid overwhelming target servers.
    
    Attributes:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
        last_request_time: Timestamp of last request
    """
    
    def __init__(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """
        Initialize rate limiter.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        
        Raises:
            ValueError: If min_delay > max_delay or delays are negative
        """
        if min_delay < 0 or max_delay < 0:
            raise ValueError("Delays must be non-negative")
        if min_delay > max_delay:
            raise ValueError("min_delay must be <= max_delay")
        
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: float = 0.0
        self._lock = asyncio.Lock()
    
    async def wait(self) -> float:
        """
        Apply random delay before next request.
        
        This method should be called before each HTTP request to enforce
        rate limiting. It calculates a random delay within the configured
        range and sleeps for that duration.
        
        Returns:
            Actual delay applied in seconds
        
        Example:
            >>> limiter = RateLimiter(min_delay=0.5, max_delay=2.0)
            >>> delay = await limiter.wait()
            >>> print(f"Waited {delay:.2f} seconds")
        """
        async with self._lock:
            # Calculate random delay
            delay = random.uniform(self.min_delay, self.max_delay)
            
            # Apply delay
            await asyncio.sleep(delay)
            
            # Update last request time
            self.last_request_time = time.time()
            
            return delay
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with min_delay, max_delay, and last_request_time
        """
        return {
            'min_delay': self.min_delay,
            'max_delay': self.max_delay,
            'last_request_time': self.last_request_time,
        }
    
    def __repr__(self) -> str:
        return f"RateLimiter(min_delay={self.min_delay}, max_delay={self.max_delay})"
