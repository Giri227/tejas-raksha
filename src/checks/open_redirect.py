"""Security check for open redirect vulnerabilities."""

from datetime import datetime
from typing import List
from urllib.parse import urlparse, parse_qs, urlencode

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


# Common redirect parameter names
REDIRECT_PARAMS = [
    "redirect",
    "url",
    "next",
    "return",
    "returnUrl",
    "return_url",
    "returnurl",
    "goto",
    "target",
    "destination",
    "redir",
    "redirect_uri",
    "redirectUri",
    "continue",
    "out",
    "view",
    "to",
]

# Test domains for open redirect detection
TEST_DOMAINS = [
    "http://evil.example.com",
    "https://attacker.example.com",
    "//evil.example.com",
]


class OpenRedirectCheck(BaseCheck):
    """
    Check for open redirect vulnerabilities.
    
    Tests URL parameters that look like redirect targets to see if they
    allow redirection to arbitrary external domains.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="Open Redirect Detection",
            description="Tests for open redirect vulnerabilities in URL parameters",
            category="Open Redirect",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute open redirect check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for open redirect vulnerabilities
        """
        findings = []
        
        # Filter URLs with query parameters
        urls_with_params = {url for url in context.urls if '?' in url}
        
        logger.info(f"Testing {len(urls_with_params)} URLs for open redirect vulnerabilities")
        
        for url in urls_with_params:
            url_findings = await self._test_url(url, context)
            findings.extend(url_findings)
        
        return findings
    
    async def _test_url(self, url: str, context: CheckContext) -> List[Finding]:
        """
        Test URL for open redirect vulnerabilities.
        
        Args:
            url: URL to test
            context: CheckContext with fetcher
        
        Returns:
            List of findings for this URL
        """
        findings = []
        
        try:
            # Parse URL and extract parameters
            parsed = urlparse(url)
            params = parse_qs(parsed.query, keep_blank_values=True)
            
            if not params:
                return findings
            
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # Check each parameter
            for param_name in params.keys():
                # Check if parameter name suggests it's a redirect parameter
                if param_name.lower() in REDIRECT_PARAMS:
                    # Test with external domains
                    for test_domain in TEST_DOMAINS[:1]:  # Test with first domain
                        finding = await self._test_redirect_parameter(
                            base_url, params, param_name, test_domain, context
                        )
                        if finding:
                            findings.append(finding)
                            break  # Found vulnerability, no need to test more domains
        
        except Exception as e:
            logger.debug(f"Error testing open redirect for {url}: {e}")
        
        return findings
    
    async def _test_redirect_parameter(
        self,
        base_url: str,
        params: dict,
        param_name: str,
        test_domain: str,
        context: CheckContext
    ) -> Finding | None:
        """
        Test a redirect parameter with an external domain.
        
        Args:
            base_url: Base URL without query string
            params: Dictionary of parameters
            param_name: Parameter to test
            test_domain: External domain to test with
            context: CheckContext with fetcher
        
        Returns:
            Finding if open redirect detected, None otherwise
        """
        try:
            # Build test URL with external domain
            test_params = params.copy()
            test_params[param_name] = [test_domain]
            
            # Flatten parameters
            flat_params = {k: v[0] if isinstance(v, list) else v for k, v in test_params.items()}
            query_string = urlencode(flat_params)
            test_url = f"{base_url}?{query_string}"
            
            # Fetch URL (will follow redirects)
            result = await context.fetcher.fetch(test_url)
            
            if result.is_error:
                return None
            
            # Check if final URL is the external domain
            final_domain = urlparse(result.url).netloc
            test_domain_parsed = urlparse(test_domain).netloc
            
            if final_domain and test_domain_parsed and final_domain == test_domain_parsed:
                logger.warning(f"Open redirect found: {base_url} (parameter: {param_name})")
                
                return Finding(
                    severity=Severity.MEDIUM,
                    title="Open Redirect Vulnerability",
                    url=test_url,
                    description=(
                        f"An open redirect vulnerability was detected in the '{param_name}' parameter. "
                        f"The application redirects to user-supplied URLs without validation, "
                        f"allowing redirection to arbitrary external domains. "
                        f"Test URL '{test_url}' successfully redirected to '{result.url}'. "
                        f"Attackers can exploit this to create convincing phishing URLs that appear "
                        f"to originate from the legitimate domain but redirect victims to malicious sites."
                    ),
                    remediation=(
                        "Implement a whitelist of allowed redirect destinations. "
                        "Validate that redirect URLs belong to trusted domains only. "
                        "Use indirect references (IDs) instead of URLs for redirect targets. "
                        "If external redirects are necessary, display a warning page before redirecting. "
                        "Implement same-origin policy for redirects where possible. "
                        "Avoid using user-supplied input directly in redirect logic."
                    ),
                    category=self.metadata.category,
                    check_name=self.metadata.name,
                    timestamp=datetime.now(),
                    metadata={
                        'vulnerable_parameter': param_name,
                        'test_domain': test_domain,
                        'final_url': result.url,
                        'base_url': base_url,
                    }
                )
        
        except Exception as e:
            logger.debug(f"Error testing redirect parameter {param_name}: {e}")
        
        return None
