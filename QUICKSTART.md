# Quick Start Guide

Get started with the Agriculture Web Portal Security Scanner in 5 minutes!

## 1. Install (2 minutes)

```bash
# Navigate to project directory
cd agri-scanner

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install scanner
pip install -e .
```

## 2. Verify Installation (30 seconds)

```bash
agri-scanner --version
```

You should see: `agri-scanner, version 1.0.0`

## 3. Run Your First Scan (2 minutes)

```bash
agri-scanner scan https://example.com
```

This will:
1. Show an ethical usage warning (confirm with 'y')
2. Crawl the website
3. Run security checks
4. Generate an HTML report in `./reports/`

## 4. View Results (30 seconds)

```bash
# Windows
start reports\scan_report_*.html

# Linux
xdg-open reports/scan_report_*.html

# Mac
open reports/scan_report_*.html
```

## 5. Try Advanced Features

### Deeper Scan
```bash
agri-scanner scan https://example.com -d 3 -c 20
```

### Multiple Report Formats
```bash
agri-scanner scan https://example.com -f html -f json -f csv
```

### Authenticated Scan
```bash
agri-scanner scan https://example.com \
  --auth-type basic \
  --auth-user admin \
  --auth-pass password
```

### Verbose Output
```bash
agri-scanner scan https://example.com -v
```

### Custom Configuration
```bash
# Copy example config
cp config.yaml my-config.yaml

# Edit my-config.yaml with your settings

# Run with config
agri-scanner scan https://example.com --config my-config.yaml
```

## Common Commands

```bash
# Basic scan
agri-scanner scan <URL>

# Help
agri-scanner --help
agri-scanner scan --help

# Skip ethical warning (only if authorized!)
agri-scanner scan <URL> --no-warning

# Custom output directory
agri-scanner scan <URL> -o ./my-reports

# Enable specific checks only
agri-scanner scan <URL> --enable-check XSSCheck --enable-check SensitiveFilesCheck

# Disable specific checks
agri-scanner scan <URL> --disable-check DirectoryListingCheck
```

## Understanding Reports

### HTML Report Sections

1. **Executive Summary**
   - Findings count by severity
   - Visual charts
   - Scan statistics

2. **Detailed Findings**
   - Filterable table
   - Complete vulnerability details
   - Remediation guidance

### Severity Levels

- 🔴 **HIGH**: Critical vulnerabilities (immediate action required)
- 🟡 **MEDIUM**: Significant issues (address soon)
- 🔵 **LOW**: Minor issues (best practices)
- ⚪ **INFO**: Informational findings

## Next Steps

1. **Read the User Manual**: `docs/USER_MANUAL.md`
2. **Explore Examples**: `examples/` directory
3. **Customize Configuration**: Edit `config.yaml`
4. **Learn Plugin Development**: `docs/PLUGIN_DEVELOPMENT.md`

## Troubleshooting

### "Command not found: agri-scanner"

Make sure virtual environment is activated:
```bash
# Check if activated (should show (.venv) in prompt)
which python  # Linux/Mac
where python  # Windows

# If not activated, activate it
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### "Permission denied" errors

Don't use `sudo` with pip in virtual environment. Just ensure venv is activated.

### "Connection refused" errors

- Verify target URL is accessible
- Check firewall settings
- Try increasing timeout: `--timeout 30`

## Important Reminders

⚠️ **Always get authorization before scanning!**

- Only scan websites you own or have permission to test
- Unauthorized scanning may be illegal
- Use findings responsibly
- Practice responsible disclosure

## Getting Help

- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **Issues**: GitHub Issues
- **Contributing**: `CONTRIBUTING.md`

## Quick Reference Card

```
Installation:
  pip install -r requirements.txt && pip install -e .

Basic Scan:
  agri-scanner scan <URL>

Options:
  -d, --depth          Crawl depth (default: 2)
  -c, --concurrency    Concurrent requests (default: 10)
  -o, --output         Output directory
  -f, --format         Report format (html/json/csv)
  -v, --verbose        Verbose output
  --config             Configuration file

Authentication:
  --auth-type          basic or digest
  --auth-user          Username
  --auth-pass          Password

Custom:
  -H, --header         Custom header
  -C, --cookie         Custom cookie
  --enable-check       Enable specific check
  --disable-check      Disable specific check

Help:
  agri-scanner --help
  agri-scanner scan --help
```

---

**Ready to scan?** Run: `agri-scanner scan https://example.com`

For detailed documentation, see `docs/USER_MANUAL.md`
