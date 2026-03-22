"""Security check for server header analysis."""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


# Known vulnerable versions (simplified database)
VULNERABLE_VERSIONS = {
    "Apache": ["2.2", "2.0", "1.3"],
    "nginx": ["1.10", "1.9", "1.8", "1.7", "1.6"],
    "Microsoft-IIS": ["7.0", "6.0", "5.0"],
    "PHP": ["5.6", "5.5", "5.4", "5.3", "5.2", "7.0", "7.1"],
}


class ServerHeadersCheck(BaseCheck):
    """
    Check for server version disclosure and known vulnerable versions.
    
    Analyzes Server and X-Powered-By headers to detect version information
    disclosure and identify potentially vulnerable server software versions.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="Server Header Analysis",
            description="Detects server version disclosure and known vulnerable server versions",
            category="Information Disclosure",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute server headers check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for server header issues
        """
        findings = []
        checked_servers = set()
        
        logger.info(f"Analyzing server headers for {len(context.urls)} URLs")
        
        # Sample URLs to check (don't need to check every URL)
        sample_urls = list(context.urls)[:10]  # Check first 10 URLs
        
        for url in sample_urls:
            try:
                result = await context.fetcher.fetch(url)
                
                if result.is_error:
                    continue
                
                # Extract headers
                server_header = result.headers.get('server', '')
                powered_by_header = result.headers.get('x-powered-by', '')
                
                # Skip if no headers or already checked this combination
                header_combo = (server_header, powered_by_header)
                if not server_header and not powered_by_header:
                    continue
                if header_combo in checked_servers:
                    continue
                
                checked_servers.add(header_combo)
                
                # Check Server header
                if server_header:
                    finding = self._check_server_header(url, server_header)
                    if finding:
                        findings.append(finding)
                
                # Check X-Powered-By header
                if powered_by_header:
                    finding = self._check_powered_by_header(url, powered_by_header)
                    if finding:
                        findings.append(finding)
            
            except Exception as e:
                logger.debug(f"Error checking headers for {url}: {e}")
        
        return findings
    
    def _check_server_header(self, url: str, server_header: str) -> Finding | None:
        """
        Check Server header for version disclosure and vulnerabilities.
        
        Args:
            url: URL where header was found
            server_header: Server header value
        
        Returns:
            Finding if issue detected, None otherwise
        """
        # Parse server name and version
        server_name, version = self._parse_server_header(server_header)
        
        if not server_name:
            return None
        
        # Check if version is disclosed
        if version:
            # Check if it's a known vulnerable version
            is_vulnerable, vuln_info = self._is_vulnerable_version(server_name, version)
            
            if is_vulnerable:
                logger.warning(
                    f"Vulnerable server version detected: {server_name} {version} at {url}"
                )
                return Finding(
                    severity=Severity.MEDIUM,
                    title="Known Vulnerable Server Version",
                    url=url,
                    description=(
                        f"The server is running {server_name} version {version}, "
                        f"which is known to have security vulnerabilities. "
                        f"The Server header discloses: '{server_header}'. "
                        f"{vuln_info}"
                    ),
                    remediation=(
                        f"Upgrade {server_name} to the latest stable version. "
                        f"Additionally, configure the server to suppress version information "
                        f"in the Server header to reduce information disclosure."
                    ),
                    category=self.metadata.category,
                    check_name=self.metadata.name,
                    timestamp=datetime.now(),
                    metadata={
                        'server_header': server_header,
                        'server_name': server_name,
                        'version': version,
                    }
                )
            else:
                # Version disclosed but not known vulnerable
                logger.info(f"Server version disclosed: {server_name} {version} at {url}")
                return Finding(
                    severity=Severity.LOW,
                    title="Server Version Disclosure",
                    url=url,
                    description=(
                        f"The server discloses its version in the Server header: '{server_header}'. "
                        f"This information can help attackers identify potential vulnerabilities "
                        f"specific to this version of {server_name}."
                    ),
                    remediation=(
                        f"Configure {server_name} to suppress version information in headers. "
                        f"For Apache: Set 'ServerTokens Prod' and 'ServerSignature Off'. "
                        f"For Nginx: Set 'server_tokens off;'. "
                        f"For IIS: Remove version headers using URL Rewrite module."
                    ),
                    category=self.metadata.category,
                    check_name=self.metadata.name,
                    timestamp=datetime.now(),
                    metadata={
                        'server_header': server_header,
                        'server_name': server_name,
                        'version': version,
                    }
                )
        
        return None
    
    def _check_powered_by_header(self, url: str, powered_by: str) -> Finding | None:
        """
        Check X-Powered-By header for version disclosure.
        
        Args:
            url: URL where header was found
            powered_by: X-Powered-By header value
        
        Returns:
            Finding if issue detected, None otherwise
        """
        logger.info(f"Technology disclosed via X-Powered-By: {powered_by} at {url}")
        
        return Finding(
            severity=Severity.LOW,
            title="Technology Disclosure via X-Powered-By Header",
            url=url,
            description=(
                f"The server discloses technology information via the X-Powered-By header: '{powered_by}'. "
                f"This header reveals details about the server-side technology stack, "
                f"which can help attackers identify potential attack vectors."
            ),
            remediation=(
                "Remove or suppress the X-Powered-By header. "
                "For PHP: Set 'expose_php = Off' in php.ini. "
                "For ASP.NET: Remove the header in web.config or Global.asax. "
                "For Express.js: Use app.disable('x-powered-by')."
            ),
            category=self.metadata.category,
            check_name=self.metadata.name,
            timestamp=datetime.now(),
            metadata={
                'powered_by_header': powered_by,
            }
        )
    
    def _parse_server_header(self, server_header: str) -> Tuple[str, Optional[str]]:
        """
        Parse server name and version from Server header.
        
        Args:
            server_header: Server header value
        
        Returns:
            Tuple of (server_name, version) or (server_name, None)
        """
        # Common patterns: "Apache/2.4.41", "nginx/1.18.0", "Microsoft-IIS/10.0"
        match = re.match(r'([A-Za-z\-]+)(?:/([0-9.]+))?', server_header)
        
        if match:
            server_name = match.group(1)
            version = match.group(2)
            return (server_name, version)
        
        return (server_header, None)
    
    def _is_vulnerable_version(self, server_name: str, version: str) -> Tuple[bool, str]:
        """
        Check if server version is known to be vulnerable.
        
        Args:
            server_name: Server software name
            version: Version string
        
        Returns:
            Tuple of (is_vulnerable, vulnerability_info)
        """
        if server_name not in VULNERABLE_VERSIONS:
            return (False, "")
        
        vulnerable_versions = VULNERABLE_VERSIONS[server_name]
        
        # Check if version starts with any vulnerable version prefix
        for vuln_version in vulnerable_versions:
            if version.startswith(vuln_version):
                info = (
                    f"Version {version} is outdated and may contain known security vulnerabilities. "
                    f"Please consult the {server_name} security advisories for specific CVEs."
                )
                return (True, info)
        
        return (False, "")
