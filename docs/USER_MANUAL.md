# User Manual

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Configuration](#configuration)
5. [Understanding Reports](#understanding-reports)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Getting Started

### Installation

```bash
# Navigate to project directory
cd agri-scanner

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
agri-scanner --version
```

### First Scan

Run your first security scan:

```bash
agri-scanner scan https://example.com
```

This will:
1. Display an ethical usage warning
2. Crawl the website (depth 2)
3. Run all security checks
4. Generate an HTML report in `./reports/`

## Basic Usage

### Simple Scan

```bash
agri-scanner scan https://example.com
```

### Specify Output Directory

```bash
agri-scanner scan https://example.com -o ./my-reports
```

### Generate Multiple Report Formats

```bash
agri-scanner scan https://example.com -f html -f json -f csv
```

### Verbose Output

```bash
agri-scanner scan https://example.com -v
```

### Deep Scan

```bash
agri-scanner scan https://example.com -d 3 -c 20
```

## Advanced Features

### Authentication

#### HTTP Basic Authentication

```bash
agri-scanner scan https://example.com \
  --auth-type basic \
  --auth-user admin \
  --auth-pass password123
```

#### HTTP Digest Authentication

```bash
agri-scanner scan https://example.com \
  --auth-type digest \
  --auth-user admin \
  --auth-pass password123
```

### Custom Headers

```bash
agri-scanner scan https://example.com \
  -H "Authorization: Bearer token123" \
  -H "X-API-Key: myapikey"
```

### Custom Cookies

```bash
agri-scanner scan https://example.com \
  -C "session_id=abc123" \
  -C "auth_token=xyz789"
```

### Subdomain Scanning

```bash
agri-scanner scan https://example.com --follow-subdomains
```

### Rate Limiting

```bash
# Slower, more polite
agri-scanner scan https://example.com --delay-min 1.0 --delay-max 3.0

# Faster (use with caution)
agri-scanner scan https://example.com --delay-min 0.1 --delay-max 0.5
```

### Ignore Robots.txt

```bash
# Use only with authorization!
agri-scanner scan https://example.com --no-robots
```

### Enable/Disable Specific Checks

```bash
# Enable only specific checks
agri-scanner scan https://example.com \
  --enable-check SensitiveFilesCheck \
  --enable-check XSSCheck

# Disable specific checks
agri-scanner scan https://example.com \
  --disable-check DirectoryListingCheck
```

### JavaScript Rendering

For JavaScript-heavy sites (requires Playwright):

```bash
# Install Playwright first
pip install playwright
playwright install chromium

# Run scan with JS rendering
agri-scanner scan https://example.com --js-render
```

## Configuration

### Configuration File

Create `config.yaml`:

```yaml
# Target (can be overridden by CLI)
target_url: "https://example.com"

# Crawl settings
max_depth: 2
concurrency: 10
follow_subdomains: false

# Rate limiting
delay_min: 0.5
delay_max: 2.0

# Robots.txt
respect_robots: true

# Authentication
auth_type: null  # 'basic' or 'digest'
auth_user: null
auth_pass: null

# Custom headers
custom_headers:
  X-API-Key: "your-api-key"

# Custom cookies
custom_cookies:
  session_id: "abc123"

# Output
output_dir: "./reports"
report_formats:
  - html
  - json

# Checks
enabled_checks: null  # null = all checks
disabled_checks: null

# Logging
verbose: false
```

Use configuration file:

```bash
agri-scanner scan https://example.com --config config.yaml
```

### Configuration Precedence

Settings are applied in this order (highest to lowest priority):

1. CLI arguments
2. Configuration file
3. Default values

Example:
```bash
# config.yaml has max_depth: 2
# This command uses depth 3 (CLI overrides config)
agri-scanner scan https://example.com --config config.yaml -d 3
```

## Understanding Reports

### HTML Report

Interactive report with:

**Executive Summary**
- Findings count by severity
- Visual severity chart
- Scan statistics

**Detailed Findings Table**
- Filterable by severity
- Sortable columns
- Complete finding details
- Remediation guidance

**Features**
- Responsive design (mobile-friendly)
- No external dependencies
- Print-friendly
- Interactive filtering

### JSON Report

Machine-readable format:

```json
{
  "scan_metadata": {
    "target_url": "https://example.com",
    "scan_date": "2024-01-15T10:30:45",
    "duration": 45.23,
    "pages_crawled": 25,
    "pages_discovered": 30
  },
  "findings": [
    {
      "severity": "High",
      "title": "Exposed .git Directory",
      "url": "https://example.com/.git/HEAD",
      "description": "...",
      "remediation": "...",
      "category": "Information Disclosure"
    }
  ],
  "statistics": {
    "total_findings": 15,
    "by_severity": {
      "High": 3,
      "Medium": 7,
      "Low": 5
    }
  }
}
```

### CSV Report

Spreadsheet format with columns:
- Severity
- Title
- URL
- Description
- Remediation
- Category
- Check Name
- Timestamp

Import into Excel, Google Sheets, or any spreadsheet application.

## Troubleshooting

### Connection Errors

**Problem:** "Connection refused" or "Connection timeout"

**Solutions:**
- Verify target URL is accessible
- Check firewall settings
- Increase timeout: `--timeout 30`
- Check network connectivity

### SSL/TLS Errors

**Problem:** "SSL certificate verification failed"

**Solutions:**
- Ensure target has valid SSL certificate
- Check system time is correct
- Update CA certificates

### Rate Limiting

**Problem:** "Too many requests" or 429 errors

**Solutions:**
- Increase delays: `--delay-min 2.0 --delay-max 5.0`
- Reduce concurrency: `-c 5`
- Check robots.txt for crawl-delay directive

### Memory Issues

**Problem:** High memory usage

**Solutions:**
- Reduce crawl depth: `-d 1`
- Reduce concurrency: `-c 5`
- Limit scope (don't use --follow-subdomains)

### Permission Denied

**Problem:** "Permission denied" when writing reports

**Solutions:**
- Check output directory permissions
- Use different output directory: `-o ~/reports`
- Run with appropriate permissions

## Best Practices

### 1. Always Get Authorization

**Before scanning:**
- Obtain written permission from website owner
- Verify scope of testing
- Understand legal implications
- Document authorization

### 2. Start with Conservative Settings

```bash
# Good first scan
agri-scanner scan https://example.com -d 2 -c 5
```

### 3. Use Configuration Files

For repeated scans, use configuration files:
- Consistent settings
- Easy to share with team
- Version control friendly
- Documented configuration

### 4. Review Reports Carefully

- Verify findings manually
- Understand false positives
- Prioritize by severity
- Document remediation

### 5. Respect Rate Limits

- Use appropriate delays
- Respect robots.txt
- Monitor server load
- Scan during off-peak hours

### 6. Secure Credentials

- Never commit credentials to version control
- Use environment variables
- Rotate credentials after testing
- Use least-privilege accounts

### 7. Document Your Scans

Keep records of:
- Scan date and time
- Configuration used
- Findings discovered
- Remediation actions
- Authorization documentation

### 8. Regular Scanning

- Schedule periodic scans
- Scan after major changes
- Track findings over time
- Monitor for regressions

### 9. Responsible Disclosure

If you find vulnerabilities:
- Report to website owner privately
- Allow time for remediation
- Follow responsible disclosure guidelines
- Don't publicly disclose until fixed

### 10. Stay Updated

- Keep scanner updated
- Review new security checks
- Follow security news
- Update dependencies regularly

## Command Reference

### Quick Reference

```bash
# Basic scan
agri-scanner scan <URL>

# Deep scan
agri-scanner scan <URL> -d 3 -c 20

# Authenticated scan
agri-scanner scan <URL> --auth-type basic --auth-user USER --auth-pass PASS

# Multiple formats
agri-scanner scan <URL> -f html -f json -f csv

# With config file
agri-scanner scan <URL> --config config.yaml

# Verbose output
agri-scanner scan <URL> -v

# Custom output directory
agri-scanner scan <URL> -o ./my-reports

# Follow subdomains
agri-scanner scan <URL> --follow-subdomains

# Custom rate limiting
agri-scanner scan <URL> --delay-min 1.0 --delay-max 3.0

# Enable specific checks
agri-scanner scan <URL> --enable-check XSSCheck --enable-check SensitiveFilesCheck

# Disable specific checks
agri-scanner scan <URL> --disable-check DirectoryListingCheck
```

### All Options

```
Usage: agri-scanner scan [OPTIONS] TARGET_URL

Options:
  -d, --depth INTEGER            Maximum crawl depth (default: 2)
  -c, --concurrency INTEGER      Concurrent requests (default: 10)
  --follow-subdomains            Follow subdomains
  --delay-min FLOAT              Min delay between requests (default: 0.5)
  --delay-max FLOAT              Max delay between requests (default: 2.0)
  --no-robots                    Ignore robots.txt
  --js-render                    Enable JavaScript rendering
  --js-timeout INTEGER           JS timeout in seconds (default: 5)
  --auth-type [basic|digest]     Authentication type
  --auth-user TEXT               Authentication username
  --auth-pass TEXT               Authentication password
  -H, --header TEXT              Custom header
  -C, --cookie TEXT              Custom cookie
  --timeout INTEGER              Request timeout (default: 10)
  -o, --output PATH              Output directory (default: ./reports)
  -f, --format [html|json|csv|all]  Report format (default: html)
  --enable-check TEXT            Enable specific check
  --disable-check TEXT           Disable specific check
  --config PATH                  Configuration file
  -v, --verbose                  Verbose logging
  --no-warning                   Skip ethical warning
  --help                         Show help message
```

## Support

### Getting Help

- Documentation: `docs/` directory
- GitHub Issues: Report bugs and request features
- Examples: `examples/` directory

### Reporting Issues

When reporting issues, include:
- Scanner version
- Command used
- Error message
- Target URL (if public)
- Operating system
- Python version

### Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.

## Legal and Ethical Considerations

### Legal Requirements

- Obtain written authorization before scanning
- Comply with local laws and regulations
- Respect terms of service
- Follow responsible disclosure practices

### Ethical Guidelines

- Only scan authorized targets
- Don't exploit vulnerabilities
- Report findings responsibly
- Respect privacy and data
- Use findings to improve security

### Disclaimer

This tool is for authorized security testing only. Users are responsible for ensuring proper authorization and compliance with applicable laws. The authors assume no liability for misuse.

## Appendix

### Security Check Reference

1. **SensitiveFilesCheck** (HIGH): Exposed .git, .env, backups
2. **DirectoryListingCheck** (MEDIUM): Directory listing enabled
3. **ServerHeadersCheck** (LOW/MEDIUM): Version disclosure
4. **XSSCheck** (HIGH): Reflected XSS in forms
5. **ErrorDisclosureCheck** (MEDIUM): Verbose error messages
6. **HTTPSConfigCheck** (LOW/MEDIUM): HTTPS misconfigurations
7. **OpenRedirectCheck** (MEDIUM): Open redirect vulnerabilities
8. **SecurityHeadersCheck** (LOW/MEDIUM): Missing security headers

### Severity Levels

- **HIGH**: Critical vulnerabilities requiring immediate attention
- **MEDIUM**: Significant issues that should be addressed soon
- **LOW**: Minor issues and best practice violations
- **INFO**: Informational findings and recommendations

### Common Use Cases

**Development Testing**
```bash
agri-scanner scan http://localhost:3000 -d 2 -v
```

**Staging Environment**
```bash
agri-scanner scan https://staging.example.com --config staging-config.yaml
```

**Production Scan**
```bash
agri-scanner scan https://example.com -d 3 -c 5 --delay-min 1.0 -f all
```

**API Testing**
```bash
agri-scanner scan https://api.example.com \
  -H "Authorization: Bearer token" \
  --enable-check SecurityHeadersCheck
```

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15
