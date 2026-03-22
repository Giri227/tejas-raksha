"""Security check for HTTPS configuration issues."""

from datetime import datetime
from typing import List
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


class HTTPSConfigCheck(BaseCheck):
    """
    Check for HTTPS configuration issues.
    
    Detects missing HSTS headers and mixed content (HTTP resources on HTTPS pages).
    Note: TLS version checking requires additional libraries and is simplified here.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="HTTPS Configuration Analysis",
            description="Checks for HTTPS security issues including missing HSTS and mixed content",
            category="Transport Security",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute HTTPS configuration check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for HTTPS issues
        """
        findings = []
        
        # Filter HTTPS URLs
        https_urls = {url for url in context.urls if url.startswith('https://')}
        
        if not https_urls:
            logger.info("No HTTPS URLs found to check")
            return findings
        
        logger.info(f"Checking HTTPS configuration for {len(https_urls)} URLs")
        
        # Check HSTS on a sample of URLs
        hsts_checked = False
        sample_urls = list(https_urls)[:5]  # Check first 5 HTTPS URLs
        
        for url in sample_urls:
            try:
                result = await context.fetcher.fetch(url)
                
                if result.is_error:
                    continue
                
                # Check HSTS header (only need to check once per domain)
                if not hsts_checked:
                    hsts_finding = self._check_hsts(url, result.headers)
                    if hsts_finding:
                        findings.append(hsts_finding)
                    hsts_checked = True
                
                # Check for mixed content
                mixed_content_finding = self._check_mixed_content(url, result.text)
                if mixed_content_finding:
                    findings.append(mixed_content_finding)
            
            except Exception as e:
                logger.debug(f"Error checking HTTPS config for {url}: {e}")
        
        return findings
    
    def _check_hsts(self, url: str, headers: dict) -> Finding | None:
        """
        Check for HSTS (Strict-Transport-Security) header.
        
        Args:
            url: URL that was checked
            headers: Response headers
        
        Returns:
            Finding if HSTS is missing, None otherwise
        """
        hsts_header = headers.get('strict-transport-security', '')
        
        if not hsts_header:
            logger.warning(f"Missing HSTS header at {url}")
            
            return Finding(
                severity=Severity.LOW,
                title="Missing HSTS Header",
                url=url,
                description=(
                    f"The HTTPS site does not set the Strict-Transport-Security (HSTS) header. "
                    f"HSTS instructs browsers to only access the site over HTTPS, preventing "
                    f"protocol downgrade attacks and cookie hijacking. Without HSTS, users may "
                    f"initially connect over HTTP before being redirected to HTTPS, creating "
                    f"a window for man-in-the-middle attacks."
                ),
                remediation=(
                    "Add the Strict-Transport-Security header to all HTTPS responses. "
                    "Recommended value: 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload'. "
                    "For Apache: Add 'Header always set Strict-Transport-Security \"max-age=31536000\"' to config. "
                    "For Nginx: Add 'add_header Strict-Transport-Security \"max-age=31536000\" always;' to config. "
                    "Consider submitting your domain to the HSTS preload list."
                ),
                category=self.metadata.category,
                check_name=self.metadata.name,
                timestamp=datetime.now(),
                metadata={
                    'hsts_header': hsts_header or 'missing',
                }
            )
        
        return None
    
    def _check_mixed_content(self, url: str, html: str) -> Finding | None:
        """
        Check for mixed content (HTTP resources on HTTPS page).
        
        Args:
            url: HTTPS URL of the page
            html: HTML content
        
        Returns:
            Finding if mixed content detected, None otherwise
        """
        if not url.startswith('https://'):
            return None
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            http_resources = []
            
            # Check images
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http://'):
                    http_resources.append(('image', src))
            
            # Check scripts
            for script in soup.find_all('script', src=True):
                src = script['src']
                if src.startswith('http://'):
                    http_resources.append(('script', src))
            
            # Check stylesheets
            for link in soup.find_all('link', href=True):
                href = link['href']
                if href.startswith('http://'):
                    http_resources.append(('stylesheet', href))
            
            # Check iframes
            for iframe in soup.find_all('iframe', src=True):
                src = iframe['src']
                if src.startswith('http://'):
                    http_resources.append(('iframe', src))
            
            if http_resources:
                resource_types = set(r[0] for r in http_resources)
                examples = [r[1] for r in http_resources[:3]]
                
                logger.warning(f"Mixed content found at {url}: {len(http_resources)} HTTP resources")
                
                return Finding(
                    severity=Severity.MEDIUM,
                    title="Mixed Content Detected",
                    url=url,
                    description=(
                        f"The HTTPS page loads {len(http_resources)} resources over insecure HTTP. "
                        f"Resource types: {', '.join(resource_types)}. "
                        f"Examples: {', '.join(examples[:2])}. "
                        f"Mixed content weakens the security of the HTTPS page, as HTTP resources "
                        f"can be intercepted and modified by attackers. Browsers may block or warn "
                        f"about mixed content, degrading user experience."
                    ),
                    remediation=(
                        "Update all resource URLs to use HTTPS instead of HTTP. "
                        "Use protocol-relative URLs (//example.com/resource) or HTTPS URLs. "
                        "Ensure all third-party resources (CDNs, analytics, etc.) support HTTPS. "
                        "Implement Content Security Policy with 'upgrade-insecure-requests' directive "
                        "to automatically upgrade HTTP requests to HTTPS."
                    ),
                    category=self.metadata.category,
                    check_name=self.metadata.name,
                    timestamp=datetime.now(),
                    metadata={
                        'http_resource_count': len(http_resources),
                        'resource_types': list(resource_types),
                        'examples': examples,
                    }
                )
        
        except Exception as e:
            logger.debug(f"Error checking mixed content for {url}: {e}")
        
        return None
