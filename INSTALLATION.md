# Installation Guide

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **RAM**: 512 MB minimum, 2 GB recommended
- **Disk Space**: 100 MB for installation, additional space for reports
- **Network**: Internet connection for scanning

### Supported Platforms
- Windows 10/11
- Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)
- macOS 11+ (Big Sur or later)

## Installation Methods

### Method 1: Install from Source (Recommended)

#### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/example/agri-scanner.git
cd agri-scanner
```

#### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Install in Development Mode

```bash
pip install -e .
```

#### Step 5: Verify Installation

```bash
agri-scanner --version
```

You should see: `agri-scanner, version 1.0.0`

### Method 2: Direct Installation

If you have the source code without git:

```bash
cd agri-scanner
python -m venv .venv

# Activate virtual environment (see above)

pip install -r requirements.txt
pip install -e .
```

## Optional Dependencies

### JavaScript Rendering

For scanning JavaScript-heavy websites:

```bash
pip install playwright
playwright install chromium
```

This installs Playwright and Chromium browser (~300 MB).

### Development Tools

For contributing to the project:

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock hypothesis black mypy
```

## Verification

### Test Installation

Run a test scan on a public test site:

```bash
agri-scanner scan http://testphp.vulnweb.com --no-warning
```

### Check Components

```python
# Test Python import
python -c "from src import Scanner; print('✓ Scanner imported successfully')"

# Test CLI
agri-scanner --help
```

## Troubleshooting

### Python Version Issues

**Problem:** "Python 3.10 or higher is required"

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.10+ from python.org
# Or use pyenv:
pyenv install 3.10.0
pyenv local 3.10.0
```

### pip Installation Fails

**Problem:** "Could not install packages"

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Virtual Environment Issues

**Problem:** "venv module not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# CentOS/RHEL
sudo yum install python3-venv
```

### Permission Errors

**Problem:** "Permission denied"

**Solution:**
```bash
# Don't use sudo with pip in virtual environment
# Instead, ensure virtual environment is activated

# Check if activated (should show (.venv) in prompt)
which python

# If not activated, activate it
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### SSL Certificate Errors

**Problem:** "SSL: CERTIFICATE_VERIFY_FAILED"

**Solution:**
```bash
# Update certificates
pip install --upgrade certifi

# Or install system certificates
# Ubuntu/Debian
sudo apt-get install ca-certificates

# macOS
/Applications/Python\ 3.10/Install\ Certificates.command
```

## Platform-Specific Instructions

### Windows

#### Prerequisites
1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Ensure "Add Python to PATH" is checked during installation

#### Installation
```powershell
# Open PowerShell or Command Prompt
cd agri-scanner
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

#### Common Issues
- If `python` command not found, try `py` instead
- If activation fails, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Linux (Ubuntu/Debian)

#### Prerequisites
```bash
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip
```

#### Installation
```bash
cd agri-scanner
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Linux (CentOS/RHEL)

#### Prerequisites
```bash
sudo yum install python3.10 python3-pip
```

#### Installation
```bash
cd agri-scanner
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### macOS

#### Prerequisites
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10
```

#### Installation
```bash
cd agri-scanner
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Docker Installation (Alternative)

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

ENTRYPOINT ["agri-scanner"]
CMD ["--help"]
```

### Build and Run

```bash
# Build image
docker build -t agri-scanner .

# Run scan
docker run --rm -v $(pwd)/reports:/app/reports agri-scanner scan https://example.com
```

## Upgrading

### Upgrade from Source

```bash
cd agri-scanner
git pull origin main
pip install -r requirements.txt --upgrade
```

### Upgrade Dependencies Only

```bash
pip install -r requirements.txt --upgrade
```

## Uninstallation

### Remove Installation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows

# Remove project directory
cd ..
rm -rf agri-scanner  # Linux/Mac
rmdir /s agri-scanner  # Windows
```

## Post-Installation

### Configuration

Create a default configuration file:

```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your preferences
```

### First Run

```bash
# Run with ethical warning
agri-scanner scan https://example.com

# Skip warning (only if authorized!)
agri-scanner scan https://example.com --no-warning
```

### Generate Reports

Reports are saved to `./reports/` by default:

```bash
# View HTML report
# Linux/Mac
open reports/scan_report_*.html

# Windows
start reports/scan_report_*.html
```

## Getting Help

### Documentation
- User Manual: `docs/USER_MANUAL.md`
- Architecture: `docs/ARCHITECTURE.md`
- Plugin Development: `docs/PLUGIN_DEVELOPMENT.md`

### Support
- GitHub Issues: Report bugs and request features
- Documentation: Check `docs/` directory
- Examples: See `examples/` directory

### Community
- Discussions: GitHub Discussions
- Contributing: See `CONTRIBUTING.md`

## Next Steps

1. Read the [User Manual](docs/USER_MANUAL.md)
2. Try example scans in `examples/`
3. Configure your first scan
4. Review generated reports
5. Customize security checks

## License

MIT License - See LICENSE file for details

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15
