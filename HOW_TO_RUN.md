# 🚀 How to Run Tejas Raksha Security Scanner

## Quick Start (3 Steps)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Giri227/tejas-raksha.git
cd tejas-raksha
```

### Step 2: Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Windows CMD:
.venv\Scripts\activate.bat

# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run a Scan

**Option A: Interactive Launcher (Easiest)**
```powershell
# Windows PowerShell
.\START_SCAN.ps1

# Windows CMD
START_SCAN.bat

# Any OS (with venv activated)
python start_scan.py
```

**Option B: Command Line**
```bash
# Quick scan (depth 1, ~2-5 minutes)
python -m src.cli.commands scan http://testphp.vulnweb.com --no-warning -d 1 -o ./reports -f html

# Comprehensive scan (depth 2, ~5-20 minutes)
python -m src.cli.commands scan http://example.com --no-warning -d 2 -o ./reports -f html -f json
```

---

## Detailed Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Internet connection

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Giri227/tejas-raksha.git
   cd tejas-raksha
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   
   **Windows PowerShell:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   
   **Windows CMD:**
   ```cmd
   .venv\Scripts\activate.bat
   ```
   
   **Linux/Mac:**
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify installation**
   ```bash
   python -m src.cli.commands --help
   ```

### Running Scans

#### Method 1: Interactive Launcher (Recommended)

The easiest way to run scans:

```powershell
.\START_SCAN.ps1
```

The launcher will ask you:
1. **Target URL** - Website to scan (e.g., http://testphp.vulnweb.com)
2. **Scan Depth** - Choose 1 (Quick), 2 (Normal), or 3 (Deep)
3. **Report Format** - Choose HTML, JSON, CSV, or combinations

Then it automatically:
- Runs the scan
- Generates reports
- Opens the HTML report in your browser

#### Method 2: Command Line

**Basic Syntax:**
```bash
python -m src.cli.commands scan <URL> [OPTIONS]
```

**Common Options:**
- `--no-warning` - Skip legal warning prompt
- `-d, --depth <N>` - Crawl depth (1=quick, 2=normal, 3=deep)
- `-o, --output <DIR>` - Output directory for reports
- `-f, --format <FORMAT>` - Report format (html, json, csv)
- `-c, --concurrency <N>` - Concurrent requests (default: 5)
- `-v, --verbose` - Enable verbose logging

**Examples:**

1. **Quick scan on test site:**
   ```bash
   python -m src.cli.commands scan http://testphp.vulnweb.com --no-warning -d 1 -o ./reports -f html
   ```

2. **Comprehensive scan with multiple formats:**
   ```bash
   python -m src.cli.commands scan http://example.com --no-warning -d 2 -o ./reports -f html -f json -f csv
   ```

3. **Authenticated scan:**
   ```bash
   python -m src.cli.commands scan https://example.com --no-warning -d 2 --auth-user admin --auth-pass password -o ./reports -f html
   ```

4. **Custom rate limiting:**
   ```bash
   python -m src.cli.commands scan http://example.com --no-warning -d 1 --delay-min 0.5 --delay-max 1.0 -o ./reports -f html
   ```

### Testing the Scanner

Test on a safe, intentionally vulnerable site:

```bash
python -m src.cli.commands scan http://testphp.vulnweb.com --no-warning -d 1 -o ./test-results -f html
```

This will detect:
- ✅ SQL Injection vulnerabilities
- ✅ XSS vulnerabilities
- ✅ Exposed sensitive files
- ✅ Missing security headers

### Understanding Scan Depths

| Depth | Time | Pages | Use Case |
|-------|------|-------|----------|
| 1 | 2-5 min | 10-30 | Quick security check |
| 2 | 5-20 min | 30-100 | Comprehensive audit |
| 3 | 20-60+ min | 100-500+ | Complete assessment |

### Viewing Reports

After a scan completes:

1. **HTML Report** - Opens automatically (or open manually from output folder)
   - Beautiful, interactive web report
   - Filterable findings table
   - Severity badges with color coding

2. **JSON Report** - Machine-readable format
   ```bash
   cat ./reports/scan_report_*.json
   ```

3. **CSV Report** - Spreadsheet-compatible
   - Open in Excel or Google Sheets

### Troubleshooting

**Issue: "Module not found" error**
```bash
# Make sure virtual environment is activated
.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: Scan takes too long**
```bash
# Use depth 1 for quick scans
python -m src.cli.commands scan <URL> --no-warning -d 1 -o ./reports -f html
```

**Issue: Connection timeout**
```bash
# Increase timeout value
python -m src.cli.commands scan <URL> --no-warning --timeout 30 -o ./reports -f html
```

**Issue: Too many requests**
```bash
# Increase delays between requests
python -m src.cli.commands scan <URL> --no-warning --delay-min 0.5 --delay-max 1.0 -o ./reports -f html
```

### Security Checks Performed

The scanner performs 9 comprehensive security checks:

1. ✅ **SQL Injection Detection** - Database injection vulnerabilities
2. ✅ **Cross-Site Scripting (XSS)** - Reflected XSS attacks
3. ✅ **Exposed Sensitive Files** - .git, .env, backups, configs
4. ✅ **Directory Listing** - Exposed directory structures
5. ✅ **Security Headers Analysis** - CSP, HSTS, X-Frame-Options, etc.
6. ✅ **Server Information Disclosure** - Version leaks
7. ✅ **Error Message Disclosure** - Verbose error messages
8. ✅ **HTTPS Configuration** - SSL/TLS validation
9. ✅ **Open Redirect** - Redirect vulnerabilities

### Legal Disclaimer

⚠️ **IMPORTANT:** Always obtain proper authorization before scanning any website.

- ✅ Only scan websites you own or have explicit permission to test
- ✅ Use http://testphp.vulnweb.com for practice
- ✅ Respect rate limits and robots.txt
- ✅ Follow responsible disclosure practices

Unauthorized security testing may be illegal in your jurisdiction.

### Getting Help

- 📖 Read the [README.md](README.md)
- 📘 Check [GETTING_STARTED.txt](GETTING_STARTED.txt)
- 📕 See [QUICK_START_GUIDE.txt](QUICK_START_GUIDE.txt)
- 📗 Review [docs/USER_MANUAL.md](docs/USER_MANUAL.md)

### Example Workflow

```bash
# 1. Clone and setup
git clone https://github.com/Giri227/tejas-raksha.git
cd tejas-raksha
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Test on vulnerable site
python -m src.cli.commands scan http://testphp.vulnweb.com --no-warning -d 1 -o ./test -f html

# 3. View report
# Report opens automatically in browser

# 4. Scan your authorized target
python -m src.cli.commands scan https://your-website.com --no-warning -d 2 -o ./scan-results -f html -f json

# 5. Review findings and take action
```

---

## Quick Reference Card

```bash
# Installation
git clone https://github.com/Giri227/tejas-raksha.git
cd tejas-raksha
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Quick Scan
python -m src.cli.commands scan <URL> --no-warning -d 1 -o ./reports -f html

# Interactive Launcher
.\START_SCAN.ps1

# Help
python -m src.cli.commands --help
python -m src.cli.commands scan --help
```

---

**🛡️ Tejas Raksha - Protecting Agriculture Web Portals**

For more information, visit: https://github.com/Giri227/tejas-raksha
