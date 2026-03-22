"""Security check for missing security headers."""

from datetime import datetime
from typing import Dict, List

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


# Security headers to check
SECURITY_HEADERS = {
    "content-security-policy": {
        "name": "Content-Security-Policy",
        "severity": Severity.LOW,
        "recommended": "default-src 'self'; script-src 'self'; object-src 'none'",
        "description": "CSP helps prevent XSS attacks by controlling which resources can be loaded",
    },
    "x-frame-options": {
        "name": "X-Frame-Options",
        "severity": Severity.LOW,
        "recommended": "DENY or SAMEORIGIN",
        "description": "Prevents clickjacking attacks by controlling if the page can be framed",
    },
    "x-content-type-options": {
        "name": "X-Content-Type-Options",
        "severity": Severity.LOW,
        "recommended": "nosniff",
        "description": "Prevents MIME-sniffing attacks",
    },
    "x-xss-protection": {
        "name": "X-XSS-Protection",
        "severity": Severity.LOW,
        "recommended": "1; mode=block",
        "description": "Enables browser XSS filtering (legacy, CSP is preferred)",
    },
    "referrer-policy": {
        "name": "Referrer-Policy",
        "severity": Severity.LOW,
        "recommended": "no-referrer or strict-origin-when-cross-origin",
        "description": "Controls how much referrer information is sent with requests",
    },
    "strict-transport-security": {
        "name": "Strict-Transport-Security",
        "severity": Severity.LOW,
        "recommended": "max-age=31536000; includeSubDomains",
        "description": "Forces HTTPS connections (HSTS)",
    },
}

# Unsafe CSP directives
UNSAFE_CSP_DIRECTIVES = ["unsafe-inline", "unsafe-eval"]


class SecurityHeadersCheck(BaseCheck):
    """
    Check for missing or misconfigured security headers.
    
    Verifies presence of important security headers and checks for
    unsafe Content Security Policy configurations.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="Security Headers Analysis",
            description="Checks for missing security headers and unsafe CSP configurations",
            category="Security Headers",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute security headers check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for missing or misconfigured headers
        """
        findings = []
        
        # Sample a few URLs to check headers (they should be consistent across the site)
        sample_urls = list(context.urls)[:5]
        
        logger.info(f"Checking security headers for {len(sample_urls)} URLs")
        
        checked_headers = False
        
        for url in sample_urls:
            try:
                result = await context.fetcher.fetch(url)
                
                if result.is_error:
                    continue
                
                # Only check once (headers should be consistent)
                if not checked_headers:
                    # Check for missing headers
                    missing_findings = self._check_missing_headers(url, result.headers)
                    findings.extend(missing_findings)
                    
                    # Check CSP for unsafe directives
                    csp_finding = self._check_csp_safety(url, result.headers)
                    if csp_finding:
                        findings.append(csp_finding)
                    
                    checked_headers = True
                    break  # Only need to check once
            
            except Exception as e:
                logger.debug(f"Error checking headers for {url}: {e}")
        
        return findings
    
    def _check_missing_headers(self, url: str, headers: Dict[str, str]) -> List[Finding]:
        """
        Check for missing security headers.
        
        Args:
            url: URL that was checked
            headers: Response headers (lowercase keys)
        
        Returns:
            List of findings for missing headers
        """
        findings = []
        missing_headers = []
        
        # Normalize header keys to lowercase
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Check each security header
        for header_key, header_info in SECURITY_HEADERS.items():
            if header_key not in headers_lower:
                missing_headers.append(header_info)
        
        if missing_headers:
            header_names = [h["name"] for h in missing_headers]
            logger.warning(f"Missing security headers at {url}: {', '.join(header_names)}")
            
            # Create one finding for all missing headers
            finding = Finding(
                severity=Severity.LOW,
                title="Missing Security Headers",
                url=url,
                description=(
                    f"The application is missing {len(missing_headers)} important security headers: "
                    f"{', '.join(header_names)}. "
                    f"Security headers provide defense-in-depth protection against various attacks. "
                    f"While not a direct vulnerability, missing headers reduce the application's "
                    f"security posture and may allow certain attacks to succeed."
                ),
                remediation=self._build_remediation(missing_headers),
                category=self.metadata.category,
                check_name=self.metadata.name,
                timestamp=datetime.now(),
                metadata={
                    'missing_headers': header_names,
                    'count': len(missing_headers),
                }
            )
            findings.append(finding)
        
        return findings
    
    def _check_csp_safety(self, url: str, headers: Dict[str, str]) -> Finding | None:
        """
        Check Content-Security-Policy for unsafe directives.
        
        Args:
            url: URL that was checked
            headers: Response headers
        
        Returns:
            Finding if unsafe CSP detected, None otherwise
        """
        # Normalize header keys
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        csp = headers_lower.get('content-security-policy', '')
        
        if not csp:
            return None
        
        # Check for unsafe directives
        unsafe_directives_found = []
        for directive in UNSAFE_CSP_DIRECTIVES:
            if directive in csp.lower():
                unsafe_directives_found.append(directive)
        
        if unsafe_directives_found:
            logger.warning(f"Unsafe CSP directives at {url}: {', '.join(unsafe_directives_found)}")
            
            return Finding(
                severity=Severity.MEDIUM,
                title="Unsafe Content Security Policy Configuration",
                url=url,
                description=(
                    f"The Content-Security-Policy header contains unsafe directives: "
                    f"{', '.join(unsafe_directives_found)}. "
                    f"The 'unsafe-inline' directive allows inline JavaScript and CSS, "
                    f"which significantly weakens CSP's protection against XSS attacks. "
                    f"The 'unsafe-eval' directive allows eval() and similar functions, "
                    f"which can be exploited for code injection. "
                    f"Current CSP: {csp[:200]}..."
                ),
                remediation=(
                    "Remove 'unsafe-inline' and 'unsafe-eval' from the CSP. "
                    "Use nonces or hashes for inline scripts and styles instead of 'unsafe-inline'. "
                    "Refactor code to avoid eval() and similar functions. "
                    "Example safe CSP: \"default-src 'self'; script-src 'self' 'nonce-{random}'; "
                    "style-src 'self' 'nonce-{random}'; object-src 'none'\""
                ),
                category=self.metadata.category,
                check_name=self.metadata.name,
                timestamp=datetime.now(),
                metadata={
                    'unsafe_directives': unsafe_directives_found,
                    'csp_header': csp,
                }
            )
        
        return None
    
    def _build_remediation(self, missing_headers: List[Dict]) -> str:
        """
        Build remediation guidance for missing headers.
        
        Args:
            missing_headers: List of missing header info dicts
        
        Returns:
            Remediation text
        """
        remediation = "Add the following security headers to all HTTP responses:\n\n"
        
        for header in missing_headers:
            remediation += (
                f"• {header['name']}: {header['recommended']}\n"
                f"  {header['description']}\n\n"
            )
        
        remediation += (
            "For Apache: Use Header directive in .htaccess or httpd.conf.\n"
            "For Nginx: Use add_header directive in nginx.conf.\n"
            "For IIS: Use custom headers in web.config or IIS Manager."
        )
        
        return remediation
