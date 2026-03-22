"""Security check for directory listing vulnerabilities."""

import re
from datetime import datetime
from typing import List
from urllib.parse import urlparse

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


# Directory listing indicators
DIRECTORY_INDICATORS = [
    "Index of /",
    "<title>Index of",
    "Directory listing for",
    "Parent Directory",
    "<h1>Index of",
]

# Apache-specific patterns
APACHE_PATTERNS = [
    r'<table>.*<th>Name</th>.*<th>Last modified</th>',
    r'<img src="/icons/folder\.gif"',
    r'<img src="/icons/back\.gif"',
    r'alt="\[DIR\]"',
]

# Nginx-specific patterns
NGINX_PATTERNS = [
    r'<h1>Index of',
    r'<hr><pre><a href="\.\./">\.\./',
    r'<a href="[^"]+/">.*</a>\s+\d{2}-[A-Za-z]{3}-\d{4}',
]


class DirectoryListingCheck(BaseCheck):
    """
    Check for directories with directory listing enabled.
    
    Detects when web servers are configured to display directory contents,
    which can expose sensitive files and application structure to attackers.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="Directory Listing Enabled",
            description="Identifies directories with directory listing enabled, exposing file structure",
            category="Information Disclosure",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute directory listing check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for directories with listing enabled
        """
        findings = []
        
        # Extract directory URLs (ending with /)
        directory_urls = {url for url in context.urls if url.endswith('/')}
        
        logger.info(f"Testing {len(directory_urls)} directory URLs for listing")
        
        for url in directory_urls:
            finding = await self._test_directory(url, context)
            if finding:
                findings.append(finding)
        
        return findings
    
    async def _test_directory(self, url: str, context: CheckContext) -> Finding | None:
        """
        Test if a directory has listing enabled.
        
        Args:
            url: Directory URL to test
            context: CheckContext with fetcher
        
        Returns:
            Finding if directory listing is enabled, None otherwise
        """
        try:
            result = await context.fetcher.fetch(url)
            
            # Only check successful responses
            if result.status_code != 200:
                return None
            
            # Check for directory listing indicators
            if not self._has_directory_listing(result.text):
                return None
            
            # Determine server type
            server_type = self._detect_server_type(result.text, result.headers)
            
            logger.warning(f"Directory listing enabled: {url} ({server_type})")
            
            return Finding(
                severity=Severity.MEDIUM,
                title="Directory Listing Enabled",
                url=url,
                description=(
                    f"Directory listing is enabled for {url}. "
                    f"The web server ({server_type}) is configured to display the contents "
                    f"of this directory, allowing anyone to browse and download files. "
                    f"This exposes the application's file structure and may reveal "
                    f"sensitive files, backup files, or configuration files."
                ),
                remediation=(
                    f"Disable directory listing in the web server configuration. "
                    f"For Apache: Add 'Options -Indexes' to .htaccess or httpd.conf. "
                    f"For Nginx: Remove or set 'autoindex off;' in nginx.conf. "
                    f"For IIS: Disable 'Directory Browsing' in IIS Manager. "
                    f"Alternatively, add an index.html file to the directory."
                ),
                category=self.metadata.category,
                check_name=self.metadata.name,
                timestamp=datetime.now(),
                metadata={
                    'server_type': server_type,
                    'status_code': result.status_code,
                }
            )
        
        except Exception as e:
            logger.debug(f"Error testing directory {url}: {e}")
        
        return None
    
    def _has_directory_listing(self, html: str) -> bool:
        """
        Check if HTML contains directory listing indicators.
        
        Args:
            html: HTML content to check
        
        Returns:
            True if directory listing is detected, False otherwise
        """
        # Check for simple string indicators
        for indicator in DIRECTORY_INDICATORS:
            if indicator in html:
                return True
        
        # Check for Apache patterns
        for pattern in APACHE_PATTERNS:
            if re.search(pattern, html, re.IGNORECASE | re.DOTALL):
                return True
        
        # Check for Nginx patterns
        for pattern in NGINX_PATTERNS:
            if re.search(pattern, html, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    def _detect_server_type(self, html: str, headers: dict) -> str:
        """
        Detect web server type from HTML and headers.
        
        Args:
            html: HTML content
            headers: Response headers
        
        Returns:
            Server type string (Apache, Nginx, IIS, or Unknown)
        """
        # Check Server header
        server_header = headers.get('server', '').lower()
        if 'apache' in server_header:
            return 'Apache'
        elif 'nginx' in server_header:
            return 'Nginx'
        elif 'iis' in server_header or 'microsoft' in server_header:
            return 'IIS'
        
        # Check HTML patterns
        for pattern in APACHE_PATTERNS:
            if re.search(pattern, html, re.IGNORECASE | re.DOTALL):
                return 'Apache'
        
        for pattern in NGINX_PATTERNS:
            if re.search(pattern, html, re.IGNORECASE | re.DOTALL):
                return 'Nginx'
        
        return 'Unknown'
