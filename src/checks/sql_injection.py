"""Security check for SQL injection vulnerabilities."""

import re
from datetime import datetime
from typing import List
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from .base import BaseCheck, CheckContext, CheckMetadata
from ..models.finding import Finding, Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SQLInjectionCheck(BaseCheck):
    """
    Check for SQL injection vulnerabilities using error-based detection.
    
    Tests GET parameters with SQL injection payloads and looks for
    database error messages in responses. This is a safe, non-destructive
    test that only checks for error disclosure.
    """
    
    # Safe SQL injection test payloads (error-based only)
    SQL_PAYLOADS = [
        "'",
        "''",
        "1'",
        "1' OR '1'='1",
        "' OR '1'='1' --",
        "' OR 1=1--",
        "admin'--",
        "1' AND '1'='2",
    ]
    
    # SQL error patterns for different databases
    SQL_ERROR_PATTERNS = [
        # MySQL
        (r"SQL syntax.*MySQL", "MySQL"),
        (r"Warning.*mysql_", "MySQL"),
        (r"valid MySQL result", "MySQL"),
        (r"MySqlClient\.", "MySQL"),
        (r"com\.mysql\.jdbc", "MySQL"),
        
        # PostgreSQL
        (r"PostgreSQL.*ERROR", "PostgreSQL"),
        (r"Warning.*\Wpg_", "PostgreSQL"),
        (r"valid PostgreSQL result", "PostgreSQL"),
        (r"Npgsql\.", "PostgreSQL"),
        (r"PG::SyntaxError", "PostgreSQL"),
        
        # Microsoft SQL Server
        (r"Driver.* SQL[\-\_\ ]*Server", "SQL Server"),
        (r"OLE DB.* SQL Server", "SQL Server"),
        (r"(\W|\A)SQL Server.*Driver", "SQL Server"),
        (r"Warning.*mssql_", "SQL Server"),
        (r"(\W|\A)SQL Server.*[0-9a-fA-F]{8}", "SQL Server"),
        (r"System\.Data\.SqlClient\.", "SQL Server"),
        
        # Oracle
        (r"\bORA-[0-9][0-9][0-9][0-9]", "Oracle"),
        (r"Oracle error", "Oracle"),
        (r"Oracle.*Driver", "Oracle"),
        (r"Warning.*\Woci_", "Oracle"),
        (r"Warning.*\Wora_", "Oracle"),
        
        # SQLite
        (r"SQLite/JDBCDriver", "SQLite"),
        (r"SQLite\.Exception", "SQLite"),
        (r"System\.Data\.SQLite\.", "SQLite"),
        (r"Warning.*sqlite_", "SQLite"),
        
        # Generic SQL errors
        (r"SQL syntax error", "Generic SQL"),
        (r"syntax error.*SQL", "Generic SQL"),
        (r"unclosed quotation mark", "Generic SQL"),
        (r"quoted string not properly terminated", "Generic SQL"),
    ]
    
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="SQL Injection (Error-Based)",
            description="Detects SQL injection vulnerabilities through database error messages",
            category="Injection",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        """
        Execute SQL injection check.
        
        Args:
            context: CheckContext with URLs and fetcher
        
        Returns:
            List of findings for SQL injection vulnerabilities
        """
        findings = []
        tested_params = set()  # Track tested parameter combinations
        
        logger.info(f"Testing {len(context.urls)} URLs for SQL injection")
        
        # Test each URL with query parameters
        for url in context.urls:
            parsed = urlparse(url)
            
            # Only test URLs with query parameters
            if not parsed.query:
                continue
            
            params = parse_qs(parsed.query, keep_blank_values=True)
            
            # Test each parameter
            for param_name in params.keys():
                # Create unique key for this URL+parameter combination
                test_key = f"{parsed.netloc}{parsed.path}:{param_name}"
                
                if test_key in tested_params:
                    continue
                
                tested_params.add(test_key)
                
                # Test with each payload
                for payload in self.SQL_PAYLOADS:
                    finding = await self._test_parameter(
                        url, param_name, payload, context
                    )
                    
                    if finding:
                        findings.append(finding)
                        # Stop testing this parameter after first finding
                        break
        
        logger.info(f"SQL injection check found {len(findings)} vulnerabilities")
        return findings
    
    async def _test_parameter(
        self,
        url: str,
        param_name: str,
        payload: str,
        context: CheckContext
    ) -> Finding | None:
        """
        Test a specific parameter with a SQL injection payload.
        
        Args:
            url: Original URL
            param_name: Parameter name to test
            payload: SQL injection payload
            context: CheckContext with fetcher
        
        Returns:
            Finding if SQL injection detected, None otherwise
        """
        try:
            # Build test URL with payload
            test_url = self._inject_payload(url, param_name, payload)
            
            # Fetch the URL
            result = await context.fetcher.fetch(test_url)
            
            if not result.is_success:
                return None
            
            # Check for SQL error patterns
            db_type, error_match = self._detect_sql_error(result.text)
            
            if db_type:
                logger.warning(
                    f"SQL injection detected in {url} parameter '{param_name}' "
                    f"(Database: {db_type})"
                )
                
                return Finding(
                    severity=Severity.HIGH,
                    title=f"SQL Injection in '{param_name}' Parameter",
                    url=url,
                    description=(
                        f"SQL injection vulnerability detected in the '{param_name}' parameter. "
                        f"When the payload '{payload}' was injected, the application returned "
                        f"a {db_type} database error message, indicating that user input is being "
                        f"directly included in SQL queries without proper sanitization. "
                        f"This vulnerability could allow an attacker to read, modify, or delete "
                        f"database contents, bypass authentication, or execute administrative operations."
                    ),
                    remediation=(
                        "Fix SQL injection vulnerabilities by:\n"
                        "1. Use parameterized queries (prepared statements) for all database operations\n"
                        "2. Never concatenate user input directly into SQL queries\n"
                        "3. Use an ORM (Object-Relational Mapping) framework that handles parameterization\n"
                        "4. Validate and sanitize all user input\n"
                        "5. Apply the principle of least privilege to database accounts\n"
                        "6. Disable detailed error messages in production\n\n"
                        "Example (PHP with PDO):\n"
                        "  // BAD: $query = \"SELECT * FROM users WHERE id = \" . $_GET['id'];\n"
                        "  // GOOD: $stmt = $pdo->prepare(\"SELECT * FROM users WHERE id = ?\");\n"
                        "  //       $stmt->execute([$_GET['id']]);"
                    ),
                    category=self.metadata.category,
                    check_name=self.metadata.name,
                    timestamp=datetime.now(),
                    metadata={
                        'parameter': param_name,
                        'payload': payload,
                        'database_type': db_type,
                        'error_snippet': error_match[:200] if error_match else '',
                        'test_url': test_url,
                    }
                )
        
        except Exception as e:
            logger.debug(f"Error testing SQL injection on {url}: {e}")
        
        return None
    
    def _inject_payload(self, url: str, param_name: str, payload: str) -> str:
        """
        Inject SQL payload into a specific parameter.
        
        Args:
            url: Original URL
            param_name: Parameter to inject into
            payload: SQL injection payload
        
        Returns:
            Modified URL with payload
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        
        # Inject payload into the target parameter
        if param_name in params:
            params[param_name] = [payload]
        
        # Rebuild query string
        new_query = urlencode(params, doseq=True)
        
        # Rebuild URL
        new_parsed = parsed._replace(query=new_query)
        return urlunparse(new_parsed)
    
    def _detect_sql_error(self, content: str) -> tuple[str | None, str | None]:
        """
        Detect SQL error messages in response content.
        
        Args:
            content: Response content to analyze
        
        Returns:
            Tuple of (database_type, error_match) or (None, None)
        """
        for pattern, db_type in self.SQL_ERROR_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return db_type, match.group(0)
        
        return None, None
