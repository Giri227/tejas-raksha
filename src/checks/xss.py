"""Security check for reflected XSS vulnerabilities."""

from datetime import datetime
from typing import List
from urllib.parse import urlencode, urlparse, parse_qs

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


# Safe XSS test payloads (only use alert/console.log, no DOM manipulation)
XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg/onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src=javascript:alert('XSS')>",
    "'-alert('XSS')-'",
    '"><script>alert("XSS")</script>',
    "<body onload=alert('XSS')>",
]

# Unique markers to detect reflection
PAYLOAD_MARKERS = [
    "XSS_TEST_MARKER_12345",
    "XSS_UNIQUE_67890",
]


class XSSCheck(BaseCheck):
    """
    Check for reflected XSS vulnerabilities in GET forms.
    
    Tests GET-based forms by injecting safe XSS payloads into parameters
    and checking if they are reflected unencoded in the response.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="Reflected XSS Detection",
            description="Tests GET forms for reflected cross-site scripting vulnerabilities",
            category="Cross-Site Scripting (XSS)",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute XSS check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for XSS vulnerabilities
        """
        findings = []
        
        logger.info(f"Testing URLs for reflected XSS vulnerabilities")
        
        # Test URLs with query parameters
        urls_with_params = {url for url in context.urls if '?' in url}
        
        logger.info(f"Found {len(urls_with_params)} URLs with parameters to test")
        
        for url in urls_with_params:
            url_findings = await self._test_url_parameters(url, context)
            findings.extend(url_findings)
        
        return findings
    
    async def _test_url_parameters(self, url: str, context: CheckContext) -> List[Finding]:
        """
        Test all parameters in a URL for XSS.
        
        Args:
            url: URL with query parameters
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
            
            # Test each parameter
            for param_name in params.keys():
                # Test with marker payload first to check for reflection
                marker_finding = await self._test_parameter(
                    base_url, params, param_name, PAYLOAD_MARKERS[0], context
                )
                
                if marker_finding:
                    # Marker was reflected, now test with actual XSS payloads
                    for payload in XSS_PAYLOADS[:3]:  # Test first 3 payloads
                        xss_finding = await self._test_parameter(
                            base_url, params, param_name, payload, context
                        )
                        if xss_finding:
                            findings.append(xss_finding)
                            break  # Found XSS, no need to test more payloads
        
        except Exception as e:
            logger.debug(f"Error testing XSS for {url}: {e}")
        
        return findings
    
    async def _test_parameter(
        self,
        base_url: str,
        params: dict,
        param_name: str,
        payload: str,
        context: CheckContext
    ) -> Finding | None:
        """
        Test a single parameter with a payload.
        
        Args:
            base_url: Base URL without query string
            params: Dictionary of parameters
            param_name: Parameter to test
            payload: Payload to inject
            context: CheckContext with fetcher
        
        Returns:
            Finding if XSS detected, None otherwise
        """
        try:
            # Build test URL with payload
            test_params = params.copy()
            test_params[param_name] = [payload]
            
            # Flatten parameters for URL encoding
            flat_params = {k: v[0] if isinstance(v, list) else v for k, v in test_params.items()}
            query_string = urlencode(flat_params)
            test_url = f"{base_url}?{query_string}"
            
            # Fetch URL
            result = await context.fetcher.fetch(test_url)
            
            if result.is_error:
                return None
            
            # Check if payload is reflected unencoded
            if self._is_reflected_unencoded(result.text, payload):
                logger.warning(f"XSS vulnerability found: {base_url} (parameter: {param_name})")
                
                return Finding(
                    severity=Severity.HIGH,
                    title="Reflected Cross-Site Scripting (XSS)",
                    url=test_url,
                    description=(
                        f"A reflected XSS vulnerability was detected in the '{param_name}' parameter. "
                        f"The application reflects user input without proper encoding or sanitization. "
                        f"The test payload '{payload}' was successfully reflected in the response. "
                        f"An attacker could exploit this to execute arbitrary JavaScript in victims' browsers, "
                        f"potentially stealing session cookies, credentials, or performing actions on behalf of the user."
                    ),
                    remediation=(
                        "Implement proper output encoding for all user-supplied input. "
                        "Use context-appropriate encoding (HTML entity encoding for HTML context, "
                        "JavaScript encoding for JavaScript context, etc.). "
                        "Implement Content Security Policy (CSP) headers to mitigate XSS impact. "
                        "Validate and sanitize all input on the server side. "
                        "Use security-focused frameworks that provide automatic XSS protection."
                    ),
                    category=self.metadata.category,
                    check_name=self.metadata.name,
                    timestamp=datetime.now(),
                    metadata={
                        'vulnerable_parameter': param_name,
                        'test_payload': payload,
                        'base_url': base_url,
                    }
                )
        
        except Exception as e:
            logger.debug(f"Error testing parameter {param_name}: {e}")
        
        return None
    
    def _is_reflected_unencoded(self, response: str, payload: str) -> bool:
        """
        Check if payload is reflected without HTML encoding.
        
        Args:
            response: HTTP response body
            payload: Payload that was injected
        
        Returns:
            True if payload is reflected unencoded, False otherwise
        """
        # Check if dangerous characters from payload appear unencoded
        dangerous_chars = ['<', '>', '"', "'", 'script', 'onerror', 'onload', 'javascript:']
        
        # Simple check: if payload contains dangerous chars and they appear in response
        for char in dangerous_chars:
            if char in payload.lower() and char in response.lower():
                # Check if it's actually unencoded (not &lt; &gt; etc.)
                if char == '<' and '&lt;' not in response:
                    return True
                elif char == '>' and '&gt;' not in response:
                    return True
                elif char in ['script', 'onerror', 'onload', 'javascript:']:
                    # These keywords appearing suggests unencoded reflection
                    if char in response.lower():
                        return True
        
        # Also check if the exact payload appears
        if payload in response:
            return True
        
        return False
