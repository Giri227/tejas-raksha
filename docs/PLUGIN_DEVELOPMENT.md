# Plugin Development Guide

## Overview

The Agriculture Web Portal Security Scanner uses a plugin architecture for security checks, making it easy to add custom vulnerability detection logic without modifying the core codebase.

## Plugin Architecture

### BaseCheck Interface

All security checks must inherit from the `BaseCheck` abstract base class:

```python
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

class BaseCheck(ABC):
    @property
    @abstractmethod
    def metadata(self) -> CheckMetadata:
        """Return check metadata."""
        pass
    
    @abstractmethod
    async def execute(self, context: CheckContext) -> List[Finding]:
        """Execute the security check."""
        pass
```

### CheckMetadata

Describes the check's properties:

```python
@dataclass
class CheckMetadata:
    name: str              # Unique check name (e.g., "SQLInjectionCheck")
    description: str       # Human-readable description
    category: str          # Category (e.g., "Injection", "Configuration")
    enabled: bool = True   # Whether check is enabled by default
```

### CheckContext

Provides access to scan resources:

```python
@dataclass
class CheckContext:
    urls: List[str]        # All discovered URLs
    fetcher: Fetcher       # HTTP client for making requests
    config: ScanConfig     # Scan configuration
```

## Creating a Custom Check

### Step 1: Create Check File

Create a new Python file in `src/checks/` directory:

```bash
touch src/checks/my_custom_check.py
```

### Step 2: Implement BaseCheck

```python
"""Custom security check for detecting XYZ vulnerability."""

from typing import List
from datetime import datetime

from .base import BaseCheck, CheckMetadata, CheckContext
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MyCustomCheck(BaseCheck):
    """
    Detects XYZ vulnerability in web applications.
    
    This check tests for [describe what it checks].
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        """Return check metadata."""
        return CheckMetadata(
            name="MyCustomCheck",
            description="Detects XYZ vulnerability",
            category="Custom Category",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute the security check.
        
        Args:
            context: Check execution context with URLs and fetcher
        
        Returns:
            List of findings discovered
        """
        findings = []
        
        logger.info(f"Running {self.metadata.name}...")
        
        # Your check logic here
        for url in context.urls:
            try:
                # Example: Fetch URL and analyze
                result = await context.fetcher.fetch(url)
                
                if result.success:
                    # Analyze response
                    if self._is_vulnerable(result.content):
                        finding = Finding(
                            severity=Severity.HIGH,
                            title="XYZ Vulnerability Detected",
                            url=url,
                            description="Detailed description of the issue",
                            remediation="How to fix this vulnerability",
                            category=self.metadata.category,
                            check_name=self.metadata.name,
                            timestamp=datetime.now(),
                            metadata={
                                'status_code': result.status_code,
                                'additional_info': 'value'
                            }
                        )
                        findings.append(finding)
            
            except Exception as e:
                logger.error(f"Error checking {url}: {e}")
                continue
        
        logger.info(f"{self.metadata.name} found {len(findings)} issue(s)")
        return findings
    
    def _is_vulnerable(self, content: str) -> bool:
        """
        Check if content indicates vulnerability.
        
        Args:
            content: Response content to analyze
        
        Returns:
            True if vulnerable, False otherwise
        """
        # Your detection logic here
        return "vulnerable_pattern" in content.lower()
```

### Step 3: Auto-Discovery

The `CheckRegistry` automatically discovers your check:
- Place file in `src/checks/` directory
- Class name must end with "Check"
- Inherits from `BaseCheck`
- No registration code needed!

## Check Development Best Practices

### 1. Safe Testing Only

**DO:**
- Read-only operations
- Safe test payloads
- Non-destructive testing

**DON'T:**
- Modify data
- Delete resources
- Exploit vulnerabilities
- Use malicious payloads

### 2. Error Handling

Always wrap check logic in try-except:

```python
async def execute(self, context: CheckContext) -> List[Finding]:
    findings = []
    
    for url in context.urls:
        try:
            # Check logic
            pass
        except Exception as e:
            logger.error(f"Error checking {url}: {e}")
            continue  # Don't let one error stop the check
    
    return findings
```

### 3. Logging

Use appropriate log levels:

```python
logger.debug(f"Checking URL: {url}")      # Detailed info
logger.info(f"Found {n} issues")          # General info
logger.warning(f"Unexpected response")    # Warnings
logger.error(f"Failed to check: {e}")     # Errors
```

### 4. Performance

- Use async/await for I/O operations
- Limit concurrent requests
- Cache results when possible
- Avoid blocking operations

```python
# Good: Concurrent requests
results = await asyncio.gather(*[
    context.fetcher.fetch(url) for url in urls[:10]
])

# Bad: Sequential requests
for url in urls:
    result = await context.fetcher.fetch(url)
```

### 5. Finding Quality

Create detailed, actionable findings:

```python
finding = Finding(
    severity=Severity.HIGH,
    title="Clear, specific title",
    url=url,
    description=(
        "Detailed description of what was found. "
        "Include specific evidence and context."
    ),
    remediation=(
        "Step-by-step guidance on how to fix. "
        "Include code examples if applicable."
    ),
    category="Appropriate category",
    check_name=self.metadata.name,
    timestamp=datetime.now(),
    metadata={
        'evidence': 'specific_value',
        'location': 'where_found',
        'additional_context': 'helpful_info'
    }
)
```

## Example Checks

### Example 1: Simple Pattern Matching

```python
class BackupFileCheck(BaseCheck):
    """Detects exposed backup files."""
    
    BACKUP_EXTENSIONS = ['.bak', '.old', '.backup', '.zip', '.tar.gz']
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="BackupFileCheck",
            description="Detects exposed backup files",
            category="Information Disclosure",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        findings = []
        
        for url in context.urls:
            for ext in self.BACKUP_EXTENSIONS:
                test_url = url.rstrip('/') + ext
                result = await context.fetcher.fetch(test_url)
                
                if result.success and result.status_code == 200:
                    findings.append(Finding(
                        severity=Severity.MEDIUM,
                        title=f"Exposed Backup File: {ext}",
                        url=test_url,
                        description=f"Backup file with extension {ext} is publicly accessible",
                        remediation="Remove backup files from web-accessible directories",
                        category=self.metadata.category,
                        check_name=self.metadata.name
                    ))
        
        return findings
```

### Example 2: Header Analysis

```python
class CORSMisconfigurationCheck(BaseCheck):
    """Detects CORS misconfigurations."""
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="CORSMisconfigurationCheck",
            description="Detects CORS misconfigurations",
            category="Configuration",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        findings = []
        
        for url in context.urls:
            # Test with malicious origin
            custom_headers = {'Origin': 'https://evil.com'}
            result = await context.fetcher.fetch(url, headers=custom_headers)
            
            if result.success:
                acao = result.headers.get('Access-Control-Allow-Origin', '')
                
                if acao == '*' or acao == 'https://evil.com':
                    findings.append(Finding(
                        severity=Severity.MEDIUM,
                        title="CORS Misconfiguration",
                        url=url,
                        description=(
                            f"Server responds with Access-Control-Allow-Origin: {acao}, "
                            "allowing any origin to access resources"
                        ),
                        remediation=(
                            "Configure CORS to only allow trusted origins. "
                            "Avoid using wildcard (*) for sensitive endpoints."
                        ),
                        category=self.metadata.category,
                        check_name=self.metadata.name,
                        metadata={'acao_header': acao}
                    ))
        
        return findings
```

### Example 3: Form-Based Testing

```python
class CSRFCheck(BaseCheck):
    """Detects missing CSRF protection."""
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="CSRFCheck",
            description="Detects missing CSRF tokens in forms",
            category="Session Management",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        findings = []
        
        for url in context.urls:
            result = await context.fetcher.fetch(url)
            
            if result.success:
                forms = context.fetcher.parser.parse_forms(result.content, url)
                
                for form in forms:
                    if form.method.upper() == 'POST':
                        # Check for CSRF token
                        has_csrf = any(
                            'csrf' in input.name.lower() or 'token' in input.name.lower()
                            for input in form.inputs
                        )
                        
                        if not has_csrf:
                            findings.append(Finding(
                                severity=Severity.MEDIUM,
                                title="Missing CSRF Protection",
                                url=url,
                                description=(
                                    f"Form at {form.action} does not include CSRF token"
                                ),
                                remediation=(
                                    "Implement CSRF tokens for all state-changing forms. "
                                    "Use framework-provided CSRF protection."
                                ),
                                category=self.metadata.category,
                                check_name=self.metadata.name,
                                metadata={'form_action': form.action}
                            ))
        
        return findings
```

## Testing Your Check

### Unit Testing

Create tests in `tests/test_checks/`:

```python
import pytest
from src.checks.my_custom_check import MyCustomCheck
from src.checks.base import CheckContext
from src.models.config import ScanConfig

@pytest.mark.asyncio
async def test_my_custom_check_detects_vulnerability(mock_fetcher):
    """Test that check detects vulnerability."""
    check = MyCustomCheck()
    
    # Setup mock fetcher
    mock_fetcher.fetch.return_value = MockResult(
        success=True,
        content="<html>vulnerable_pattern</html>",
        status_code=200
    )
    
    # Create context
    context = CheckContext(
        urls=['https://example.com'],
        fetcher=mock_fetcher,
        config=ScanConfig(target_url='https://example.com')
    )
    
    # Execute check
    findings = await check.execute(context)
    
    # Verify
    assert len(findings) == 1
    assert findings[0].severity == Severity.HIGH
```

### Integration Testing

Test with real HTTP responses:

```bash
# Run check against test target
agri-scanner scan https://test.example.com --enable-check MyCustomCheck
```

## Configuration

### Enabling/Disabling Checks

Users can control your check via CLI:

```bash
# Enable only specific checks
agri-scanner scan https://example.com --enable-check MyCustomCheck

# Disable specific checks
agri-scanner scan https://example.com --disable-check MyCustomCheck
```

Or via configuration file:

```yaml
enabled_checks:
  - MyCustomCheck
  - AnotherCheck

disabled_checks:
  - SomeCheck
```

## Severity Guidelines

Choose appropriate severity levels:

### HIGH
- Remote code execution
- SQL injection
- Authentication bypass
- Exposed sensitive data

### MEDIUM
- XSS vulnerabilities
- CSRF vulnerabilities
- Information disclosure
- Weak configurations

### LOW
- Missing security headers
- Version disclosure
- Minor misconfigurations

### INFO
- Best practice recommendations
- Informational findings
- Non-security issues

## Documentation

Document your check thoroughly:

```python
class MyCustomCheck(BaseCheck):
    """
    Detects XYZ vulnerability in web applications.
    
    This check tests for [detailed description of what it checks].
    
    Detection Method:
        1. Step one of detection
        2. Step two of detection
        3. Step three of detection
    
    References:
        - OWASP: https://owasp.org/...
        - CVE: CVE-XXXX-XXXXX
    
    Examples:
        Vulnerable code:
            [code example]
        
        Secure code:
            [code example]
    """
```

## Contributing

To contribute your check to the project:

1. Ensure it follows all best practices
2. Include comprehensive tests
3. Document thoroughly
4. Submit a pull request
5. Include example findings

## Resources

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)
- [NIST NVD](https://nvd.nist.gov/)

## Support

For questions about plugin development:
- Check existing checks in `src/checks/` for examples
- Review the architecture documentation
- Open an issue on GitHub
- Contact the development team
