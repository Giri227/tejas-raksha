"""Security check for exposed sensitive files."""

from datetime import datetime
from typing import List
from urllib.parse import urljoin, urlparse

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


# List of sensitive file paths to check
SENSITIVE_PATHS = [
    ".git/HEAD",
    ".git/config",
    ".git/index",
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".DS_Store",
    "backup.sql",
    "database.sql",
    "db_backup.sql",
    "dump.sql",
    "phpinfo.php",
    "info.php",
    "test.php",
    "wp-config.php",
    "wp-config.php.bak",
    "config.php",
    "config.php.bak",
    "configuration.php",
    ".htaccess",
    ".htpasswd",
    "web.config",
    "composer.json",
    "composer.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    ".npmrc",
    "Dockerfile",
    "docker-compose.yml",
    ".dockerignore",
    "id_rsa",
    "id_rsa.pub",
    ".ssh/id_rsa",
    "server.key",
    "server.crt",
    "privatekey.pem",
]

# Backup file patterns (will be tested with common extensions)
BACKUP_EXTENSIONS = [
    ".bak",
    ".old",
    ".backup",
    ".orig",
    ".save",
    "~",
    ".swp",
    ".swo",
    ".tmp",
]


class SensitiveFilesCheck(BaseCheck):
    """
    Check for exposed sensitive files and directories.
    
    Tests for common sensitive file paths like .git, .env, backup files,
    configuration files, and other files that should not be publicly accessible.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="Exposed Sensitive Files",
            description="Detects publicly accessible sensitive files like .git, .env, backups, and configuration files",
            category="Information Disclosure",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute sensitive files check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for exposed sensitive files
        """
        findings = []
        
        # Extract unique base URLs and directories from discovered URLs
        base_urls = self._extract_base_urls(context.urls)
        
        logger.info(f"Testing {len(base_urls)} base URLs for sensitive files")
        
        # Test each base URL
        for base_url in base_urls:
            # Test predefined sensitive paths
            for sensitive_path in SENSITIVE_PATHS:
                test_url = urljoin(base_url, sensitive_path)
                finding = await self._test_url(test_url, context)
                if finding:
                    findings.append(finding)
            
            # Test backup file patterns for discovered URLs
            for url in context.urls:
                if url.startswith(base_url):
                    for ext in BACKUP_EXTENSIONS:
                        test_url = url + ext
                        finding = await self._test_url(test_url, context)
                        if finding:
                            findings.append(finding)
        
        return findings
    
    def _extract_base_urls(self, urls: set) -> set:
        """
        Extract unique base URLs from discovered URLs.
        
        Args:
            urls: Set of discovered URLs
        
        Returns:
            Set of base URLs (scheme + netloc + path up to last /)
        """
        base_urls = set()
        
        for url in urls:
            parsed = urlparse(url)
            
            # Add root URL
            root = f"{parsed.scheme}://{parsed.netloc}/"
            base_urls.add(root)
            
            # Add directory paths
            path = parsed.path
            if path and path != '/':
                # Get directory path (everything up to last /)
                dir_path = path.rsplit('/', 1)[0] + '/'
                base_url = f"{parsed.scheme}://{parsed.netloc}{dir_path}"
                base_urls.add(base_url)
        
        return base_urls
    
    async def _test_url(self, url: str, context: CheckContext) -> Finding | None:
        """
        Test if a URL returns a sensitive file.
        
        Args:
            url: URL to test
            context: CheckContext with fetcher
        
        Returns:
            Finding if file is exposed, None otherwise
        """
        try:
            result = await context.fetcher.fetch(url)
            
            # Check if file exists (200 status with content)
            if result.status_code == 200 and len(result.content) > 0:
                logger.warning(f"Exposed sensitive file found: {url}")
                
                return Finding(
                    severity=Severity.HIGH,
                    title="Exposed Sensitive File",
                    url=url,
                    description=(
                        f"A sensitive file is publicly accessible at {url}. "
                        f"This file returned HTTP 200 status with {len(result.content)} bytes of content. "
                        f"Sensitive files can expose configuration details, credentials, source code, "
                        f"or other confidential information to attackers."
                    ),
                    remediation=(
                        "Remove the sensitive file from the web root or configure the web server "
                        "to deny access to it. For version control directories like .git, ensure "
                        "they are not deployed to production. For configuration files, move them "
                        "outside the document root or use environment variables. For backup files, "
                        "delete them or store them in a secure location outside the web root."
                    ),
                    category=self.metadata.category,
                    check_name=self.metadata.name,
                    timestamp=datetime.now(),
                    metadata={
                        'status_code': result.status_code,
                        'content_length': len(result.content),
                        'content_type': result.headers.get('content-type', 'unknown'),
                    }
                )
        
        except Exception as e:
            logger.debug(f"Error testing {url}: {e}")
        
        return None
