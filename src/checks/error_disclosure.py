"""Security check for error message disclosure."""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


# SQL error patterns
SQL_ERROR_PATTERNS = [
    (r"SQL syntax.*MySQL", "MySQL SQL Error"),
    (r"Warning.*mysql_", "MySQL Warning"),
    (r"PostgreSQL.*ERROR", "PostgreSQL Error"),
    (r"Warning.*pg_", "PostgreSQL Warning"),
    (r"ORA-\d{5}", "Oracle Error"),
    (r"Microsoft SQL Server.*error", "MSSQL Error"),
    (r"SQLite.*error", "SQLite Error"),
    (r"SQL Server.*error", "SQL Server Error"),
    (r"Unclosed quotation mark", "SQL Syntax Error"),
    (r"quoted string not properly terminated", "SQL Syntax Error"),
]

# Stack trace patterns
STACK_TRACE_PATTERNS = [
    (r"Traceback \(most recent call last\)", "Python Stack Trace"),
    (r"at .*\.java:\d+", "Java Stack Trace"),
    (r"Fatal error:.*in .*\.php on line \d+", "PHP Fatal Error"),
    (r"System\..*Exception:", ".NET Exception"),
    (r"RuntimeError:", "Python Runtime Error"),
    (r"TypeError:", "Python Type Error"),
    (r"ValueError:", "Python Value Error"),
    (r"Exception in thread", "Java Exception"),
]

# Path disclosure patterns
PATH_DISCLOSURE_PATTERNS = [
    (r"[A-Z]:\\[^<>\"]+", "Windows Path"),
    (r"/home/[^<>\"]+", "Linux Home Path"),
    (r"/var/www/[^<>\"]+", "Web Root Path"),
    (r"/usr/[^<>\"]+", "Unix System Path"),
]

# Database connection error patterns
DB_CONNECTION_PATTERNS = [
    (r"Could not connect to.*database", "Database Connection Error"),
    (r"Access denied for user", "Database Access Denied"),
    (r"Unknown database", "Unknown Database Error"),
    (r"Connection refused", "Connection Refused"),
]


class ErrorDisclosureCheck(BaseCheck):
    """
    Check for verbose error messages that disclose sensitive information.
    
    Analyzes error responses (4xx and 5xx) for SQL errors, stack traces,
    path disclosures, and database connection errors.
    """
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="Error Message Disclosure",
            description="Detects verbose error messages that expose sensitive information",
            category="Information Disclosure",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute error disclosure check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for error disclosures
        """
        findings = []
        
        logger.info(f"Testing for error disclosure vulnerabilities")
        
        # Sample URLs to test (check first 20)
        sample_urls = list(context.urls)[:20]
        
        for url in sample_urls:
            try:
                result = await context.fetcher.fetch(url)
                
                # Check error responses (4xx and 5xx)
                if result.status_code >= 400:
                    finding = self._analyze_error_response(url, result.text, result.status_code)
                    if finding:
                        findings.append(finding)
            
            except Exception as e:
                logger.debug(f"Error testing {url}: {e}")
        
        return findings
    
    def _analyze_error_response(self, url: str, response: str, status_code: int) -> Finding | None:
        """
        Analyze error response for sensitive information disclosure.
        
        Args:
            url: URL that returned the error
            response: Response body
            status_code: HTTP status code
        
        Returns:
            Finding if error disclosure detected, None otherwise
        """
        disclosures = []
        
        # Check for SQL errors
        sql_errors = self._check_patterns(response, SQL_ERROR_PATTERNS)
        if sql_errors:
            disclosures.extend(sql_errors)
        
        # Check for stack traces
        stack_traces = self._check_patterns(response, STACK_TRACE_PATTERNS)
        if stack_traces:
            disclosures.extend(stack_traces)
        
        # Check for path disclosures
        path_disclosures = self._check_patterns(response, PATH_DISCLOSURE_PATTERNS)
        if path_disclosures:
            disclosures.extend(path_disclosures)
        
        # Check for database connection errors
        db_errors = self._check_patterns(response, DB_CONNECTION_PATTERNS)
        if db_errors:
            disclosures.extend(db_errors)
        
        if not disclosures:
            return None
        
        # Create finding
        disclosure_types = ", ".join(set(d[1] for d in disclosures))
        examples = [d[0] for d in disclosures[:3]]  # First 3 examples
        
        logger.warning(f"Error disclosure found at {url}: {disclosure_types}")
        
        return Finding(
            severity=Severity.MEDIUM,
            title="Verbose Error Message Disclosure",
            url=url,
            description=(
                f"The application returns verbose error messages that disclose sensitive information. "
                f"HTTP {status_code} response contains: {disclosure_types}. "
                f"Examples of disclosed information: {', '.join(examples[:2])}. "
                f"This information can help attackers understand the application's internal structure, "
                f"technology stack, file system paths, and potential vulnerabilities."
            ),
            remediation=(
                "Implement custom error pages that display generic error messages to users. "
                "Log detailed error information server-side for debugging purposes only. "
                "Disable debug mode and verbose error reporting in production environments. "
                "Configure the web server and application framework to suppress detailed error messages. "
                "For PHP: Set 'display_errors = Off' in php.ini. "
                "For ASP.NET: Set customErrors mode='On' in web.config. "
                "For Django: Set DEBUG = False in settings.py."
            ),
            category=self.metadata.category,
            check_name=self.metadata.name,
            timestamp=datetime.now(),
            metadata={
                'status_code': status_code,
                'disclosure_types': disclosure_types,
                'examples': examples,
            }
        )
    
    def _check_patterns(self, text: str, patterns: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """
        Check text against a list of regex patterns.
        
        Args:
            text: Text to check
            patterns: List of (pattern, description) tuples
        
        Returns:
            List of (matched_text, description) tuples
        """
        matches = []
        
        for pattern, description in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                matched_text = match.group(0)[:100]  # Limit to 100 chars
                matches.append((matched_text, description))
        
        return matches
