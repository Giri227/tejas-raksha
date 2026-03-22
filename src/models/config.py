"""Configuration data model for scanner."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScanConfig:
    """
    Complete scan configuration.
    
    Attributes:
        target_url: Starting URL for the scan
        max_depth: Maximum crawl depth from starting URL
        concurrency: Maximum number of concurrent HTTP requests
        follow_subdomains: Whether to follow links to subdomains
        delay_min: Minimum delay between requests in seconds
        delay_max: Maximum delay between requests in seconds
        respect_robots: Whether to respect robots.txt directives
        js_render: Enable JavaScript rendering with Playwright
        js_timeout: Timeout for JavaScript rendering in seconds
        auth_type: Authentication type (basic, digest, or None)
        auth_user: Authentication username
        auth_pass: Authentication password
        timeout: HTTP request timeout in seconds
        user_agents: List of User-Agent strings to rotate
        custom_headers: Custom HTTP headers to include
        custom_cookies: Custom cookies to include
        output_dir: Directory for output reports
        report_formats: List of report formats to generate
        enabled_checks: List of specific checks to enable (None = all)
        disabled_checks: List of specific checks to disable
        verbose: Enable verbose logging
    """
    
    target_url: str
    
    # Crawl settings
    max_depth: int = 2
    concurrency: int = 10
    follow_subdomains: bool = False
    
    # Rate limiting
    delay_min: float = 0.5
    delay_max: float = 2.0
    
    # Robots.txt
    respect_robots: bool = True
    
    # JavaScript rendering
    js_render: bool = False
    js_timeout: int = 5
    
    # Authentication
    auth_type: Optional[str] = None
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    
    # HTTP settings
    timeout: int = 10
    user_agents: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_cookies: Dict[str, str] = field(default_factory=dict)
    
    # Output settings
    output_dir: str = "./reports"
    report_formats: List[str] = field(default_factory=lambda: ['html'])
    
    # Check settings
    enabled_checks: Optional[List[str]] = None
    disabled_checks: Optional[List[str]] = None
    
    # Logging
    verbose: bool = False
    
    def __post_init__(self) -> None:
        """Set defaults for mutable fields if not provided."""
        if not self.user_agents:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ]
    
    @classmethod
    def defaults(cls) -> 'ScanConfig':
        """
        Create configuration with all default values.
        
        Returns:
            ScanConfig instance with defaults
        """
        return cls(target_url="")
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            'target_url': self.target_url,
            'max_depth': self.max_depth,
            'concurrency': self.concurrency,
            'follow_subdomains': self.follow_subdomains,
            'delay_min': self.delay_min,
            'delay_max': self.delay_max,
            'respect_robots': self.respect_robots,
            'js_render': self.js_render,
            'js_timeout': self.js_timeout,
            'auth_type': self.auth_type,
            'timeout': self.timeout,
            'output_dir': self.output_dir,
            'report_formats': self.report_formats,
            'enabled_checks': self.enabled_checks,
            'disabled_checks': self.disabled_checks,
            'verbose': self.verbose,
        }
