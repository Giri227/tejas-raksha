# Architecture Documentation

## Overview

The Agriculture Web Portal Security Scanner is built with a modular, async-first architecture designed for high performance, extensibility, and maintainability.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                           │
│                    (Click Commands)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Scanner Controller                       │
│              (Orchestrates 3-Phase Workflow)                │
└─┬───────────────────┬───────────────────┬───────────────────┘
  │                   │                   │
  ▼                   ▼                   ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────────┐
│   Crawler   │  │    Checks    │  │    Reporter     │
│  Controller │  │   Registry   │  │   Generator     │
└──────┬──────┘  └──────┬───────┘  └────────┬────────┘
       │                │                    │
       ▼                ▼                    ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────────┐
│  Fetcher    │  │  8 Security  │  │  HTML/JSON/CSV  │
│  Parser     │  │    Checks    │  │    Reporters    │
│  Frontier   │  │   (Plugins)  │  │                 │
└─────────────┘  └──────────────┘  └─────────────────┘
       │                │                    │
       ▼                ▼                    ▼
┌─────────────────────────────────────────────────────┐
│              Utility Components                     │
│  (Validators, RateLimiter, RobotsParser, Logger)   │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. Scanner Controller (`scanner.py`)

The main orchestrator that coordinates the three-phase scan workflow:

**Phase 1 - Crawling**
- Initializes CrawlerController
- Discovers URLs from target website
- Respects depth limits and scope constraints

**Phase 2 - Security Checks**
- Initializes CheckRegistry
- Executes all enabled security checks concurrently
- Collects findings from each check

**Phase 3 - Report Generation**
- Initializes ReportGenerator
- Generates reports in configured formats
- Saves timestamped output files

**Key Features:**
- Error isolation between phases
- Comprehensive logging and progress reporting
- Performance statistics tracking
- Graceful degradation on failures

### 2. Crawler Module (`crawler/`)

#### CrawlerController (`controller.py`)
- Orchestrates the crawling process
- Manages URL queue via Frontier
- Enforces depth and scope constraints
- Controls concurrency with asyncio.Semaphore
- Processes URLs in batches

#### Fetcher (`fetcher.py`)
- Async HTTP client using httpx
- Connection pooling (100 connections, HTTP/2)
- Rate limiting integration
- Robots.txt respect
- User-Agent rotation
- Authentication support (Basic, Digest)
- Custom headers and cookies

#### Parser (`parser.py`)
- HTML parsing with BeautifulSoup4 and lxml
- Link extraction from multiple tags (a, link, script, img)
- Form parsing with input field extraction
- URL normalization and resolution

#### Frontier (`frontier.py`)
- URL queue management with deque
- Duplicate detection with set
- Depth tracking per URL
- Statistics tracking

### 3. Security Checks Module (`checks/`)

#### Plugin Architecture

**BaseCheck** (`base.py`)
- Abstract base class for all checks
- Defines standard interface: `execute(context) -> List[Finding]`
- Metadata: name, description, category, enabled status

**CheckRegistry** (`registry.py`)
- Auto-discovers check plugins from checks/ directory
- Manages check lifecycle
- Executes checks concurrently with asyncio.gather
- Isolates errors (one check failure doesn't stop others)
- Filters checks based on enabled/disabled configuration

#### Built-in Security Checks

1. **SensitiveFilesCheck**: Tests for exposed sensitive files
2. **DirectoryListingCheck**: Detects directory listing vulnerabilities
3. **ServerHeadersCheck**: Analyzes server version disclosure
4. **XSSCheck**: Tests for reflected XSS in forms
5. **ErrorDisclosureCheck**: Detects verbose error messages
6. **HTTPSConfigCheck**: Validates HTTPS configuration
7. **OpenRedirectCheck**: Tests for open redirect vulnerabilities
8. **SecurityHeadersCheck**: Verifies security headers

### 4. Reporter Module (`reporter/`)

#### ReportGenerator (`generator.py`)
- Orchestrates multiple report formats
- Coordinates HTML, JSON, and CSV reporters
- Returns paths to generated reports

#### HTMLReporter (`html_reporter.py`)
- Jinja2 template rendering
- Embeds CSS and JavaScript (no external dependencies)
- Groups findings by severity
- Interactive features (filtering, charts)

#### JSONReporter (`json_reporter.py`)
- Machine-readable JSON output
- Complete finding data with metadata
- Scan statistics and configuration

#### CSVReporter (`csv_reporter.py`)
- Spreadsheet-friendly format
- One finding per row
- Proper CSV escaping

### 5. Data Models (`models/`)

#### Finding (`finding.py`)
- Represents a security finding
- Severity levels: HIGH, MEDIUM, LOW, INFO
- Includes: title, description, remediation, URL, category
- Serialization support (to_dict, from_dict)

#### ScanResult (`scan_result.py`)
- Complete scan results container
- Includes: metadata, findings, errors
- Helper methods: get_findings_by_severity(), get_statistics()

#### ScanConfig (`config.py`)
- Complete scan configuration
- Crawl settings, rate limiting, authentication
- Output settings, check configuration
- Defaults and validation

### 6. Utility Components (`utils/`)

#### Validators (`validators.py`)
- URL validation and normalization
- Domain and subdomain checking
- Scope enforcement

#### RateLimiter (`rate_limiter.py`)
- Random delay between requests
- Configurable min/max delays
- Async-compatible

#### RobotsParser (`robots_parser.py`)
- Robots.txt parsing and caching
- User-agent matching
- Path checking

#### HTTPUtils (`http_utils.py`)
- User-Agent rotation
- Header construction
- Content type parsing

#### Logger (`logger.py`)
- Colored console output
- File logging with rotation
- Configurable log levels

## Design Patterns

### 1. Plugin Architecture
Security checks use a plugin pattern for easy extensibility:
- BaseCheck abstract class defines interface
- CheckRegistry auto-discovers plugins
- New checks can be added without modifying core code

### 2. Async/Await Throughout
All I/O operations use async/await for high performance:
- Concurrent HTTP requests
- Non-blocking file operations
- Efficient resource utilization

### 3. Dependency Injection
Components receive dependencies via constructor:
- Easy testing with mocks
- Flexible configuration
- Clear dependencies

### 4. Error Isolation
Failures are isolated to prevent cascading:
- Each check runs independently
- Phase failures don't stop the scan
- Comprehensive error logging

### 5. Strategy Pattern
Multiple report formats use strategy pattern:
- Common interface (generate method)
- Easy to add new formats
- Format selection at runtime

## Data Flow

### Scan Workflow

```
1. CLI parses arguments
   ↓
2. Load/merge configuration
   ↓
3. Create Scanner instance
   ↓
4. PHASE 1: Crawl
   - Fetch starting URL
   - Extract links
   - Add to frontier
   - Process queue (breadth-first)
   - Respect depth limit
   ↓
5. PHASE 2: Security Checks
   - Initialize CheckRegistry
   - Execute all checks concurrently
   - Collect findings
   ↓
6. PHASE 3: Report Generation
   - Create ScanResult
   - Generate reports in parallel
   - Save to output directory
   ↓
7. Display summary
```

### URL Processing Flow

```
URL → Validate → Normalize → Check Scope → Check Robots.txt
  ↓
Rate Limit → Fetch → Parse HTML → Extract Links/Forms
  ↓
Add to Frontier → Mark Visited → Continue
```

### Check Execution Flow

```
CheckRegistry.execute_all(urls)
  ↓
For each check:
  - Create CheckContext (urls, fetcher, config)
  - Execute check.execute(context)
  - Collect findings
  - Handle errors independently
  ↓
Aggregate all findings
```

## Concurrency Model

### Crawler Concurrency
- asyncio.Semaphore limits concurrent requests
- Default: 10 concurrent requests
- Configurable via --concurrency option
- Batch processing for efficiency

### Check Concurrency
- All checks run concurrently with asyncio.gather
- Each check is independent
- Error in one check doesn't affect others

### Report Generation
- Reports can be generated in parallel
- Each format is independent
- Async file I/O

## Performance Characteristics

### Throughput
- Target: 100+ pages/minute with polite settings
- Achieved through:
  - Concurrent requests
  - Connection pooling
  - HTTP/2 support
  - Efficient data structures

### Memory Usage
- URL deduplication with sets
- Streaming HTML parsing
- Limited response buffering
- Target: < 500MB for typical scans

### Startup Time
- Lazy imports where possible
- Fast configuration loading
- Target: < 2 seconds

## Security Considerations

### Safe Testing
- All checks are read-only
- No data modification
- No exploitation attempts
- Safe XSS payloads only

### Authentication
- Supports HTTP Basic and Digest
- Custom headers and cookies
- Credentials not logged

### Rate Limiting
- Polite crawling by default
- Respects robots.txt
- Random delays between requests
- Configurable limits

## Extensibility

### Adding New Security Checks

1. Create new file in `src/checks/`
2. Inherit from `BaseCheck`
3. Implement `metadata` property
4. Implement `execute(context)` method
5. Return list of `Finding` objects

Example:
```python
from .base import BaseCheck, CheckMetadata, CheckContext
from ..models.finding import Finding, Severity

class MyCustomCheck(BaseCheck):
    @property
    def metadata(self) -> CheckMetadata:
        return CheckMetadata(
            name="MyCustomCheck",
            description="Checks for custom vulnerability",
            category="Custom",
            enabled=True
        )
    
    async def execute(self, context: CheckContext) -> List[Finding]:
        findings = []
        # Your check logic here
        return findings
```

### Adding New Report Formats

1. Create new file in `src/reporter/`
2. Implement `generate(scan_result, output_dir)` method
3. Return file path
4. Register in `ReportGenerator`

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Focus on business logic

### Integration Tests
- Test component interactions
- Use test fixtures for HTTP responses
- Verify end-to-end workflows

### Property-Based Tests
- Use Hypothesis for property testing
- Test invariants and edge cases
- Validate correctness properties

## Configuration Management

### Precedence Order
1. CLI arguments (highest priority)
2. Configuration file
3. Default values (lowest priority)

### Configuration Sources
- YAML files (recommended)
- JSON files
- CLI arguments
- Programmatic configuration

## Logging Strategy

### Log Levels
- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages

### Log Outputs
- Console: Colored output for readability
- File: Timestamped log files in output directory

### Verbose Mode
- Enables DEBUG level logging
- Shows HTTP requests and responses
- Displays check execution details

## Error Handling

### Error Categories
1. **Configuration Errors**: Invalid settings, missing required fields
2. **Network Errors**: Connection failures, timeouts
3. **Parsing Errors**: Malformed HTML, invalid URLs
4. **Check Errors**: Exceptions during check execution

### Error Recovery
- Graceful degradation
- Continue scan despite errors
- Log errors for debugging
- Report errors in scan results

## Future Enhancements

### Potential Improvements
1. JavaScript rendering with Playwright
2. Database storage for scan history
3. Differential scanning (compare scans)
4. API endpoint for programmatic access
5. Web UI for scan management
6. Distributed scanning across multiple nodes
7. Machine learning for anomaly detection
8. Integration with CI/CD pipelines

## References

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [httpx Documentation](https://www.python-httpx.org/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
