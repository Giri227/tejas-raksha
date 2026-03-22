"""CLI commands for Tejas Raksha Security Scanner."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from ..models.config import ScanConfig
from ..scanner import Scanner
from ..utils.logger import get_logger

logger = get_logger(__name__)

ETHICAL_WARNING = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                        ⚠️  ETHICAL USAGE WARNING ⚠️                        ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  Tejas Raksha Security Scanner is for AUTHORIZED testing only.           ║
║                                                                           ║
║  You MUST have explicit written permission from the website owner        ║
║  before scanning any web application.                                    ║
║                                                                           ║
║  Unauthorized security testing may be ILLEGAL in your jurisdiction       ║
║  and could result in criminal prosecution.                               ║
║                                                                           ║
║  By using this tool, you agree to:                                       ║
║  • Only scan systems you own or have written authorization to test       ║
║  • Comply with all applicable laws and regulations                       ║
║  • Use findings responsibly and practice responsible disclosure          ║
║  • Not use this tool for malicious purposes                              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""


@click.group()
@click.version_option(version="1.0.0", prog_name="tejas-raksha")
def cli():
    """Tejas Raksha Security Scanner - Professional security testing tool for agriculture web portals."""
    pass


@cli.command()
@click.argument('target_url')
@click.option('--depth', '-d', default=2, type=int, 
              help='Maximum crawl depth (default: 2)')
@click.option('--concurrency', '-c', default=10, type=int,
              help='Maximum concurrent requests (default: 10)')
@click.option('--follow-subdomains', is_flag=True,
              help='Follow links to subdomains')
@click.option('--delay-min', default=0.5, type=float,
              help='Minimum delay between requests in seconds (default: 0.5)')
@click.option('--delay-max', default=2.0, type=float,
              help='Maximum delay between requests in seconds (default: 2.0)')
@click.option('--no-robots', is_flag=True,
              help='Ignore robots.txt (use with caution)')
@click.option('--js-render', is_flag=True,
              help='Enable JavaScript rendering with Playwright')
@click.option('--js-timeout', default=5, type=int,
              help='JavaScript rendering timeout in seconds (default: 5)')
@click.option('--auth-type', type=click.Choice(['basic', 'digest']),
              help='Authentication type')
@click.option('--auth-user', type=str,
              help='Authentication username')
@click.option('--auth-pass', type=str,
              help='Authentication password')
@click.option('--header', '-H', multiple=True,
              help='Custom header (format: "Name: Value")')
@click.option('--cookie', '-C', multiple=True,
              help='Custom cookie (format: "name=value")')
@click.option('--timeout', default=10, type=int,
              help='HTTP request timeout in seconds (default: 10)')
@click.option('--output', '-o', default='./reports',
              help='Output directory for reports (default: ./reports)')
@click.option('--format', '-f', 'formats', multiple=True,
              type=click.Choice(['html', 'json', 'csv', 'all']),
              default=['html'],
              help='Report format(s) to generate (default: html)')
@click.option('--enable-check', multiple=True,
              help='Enable specific security check(s)')
@click.option('--disable-check', multiple=True,
              help='Disable specific security check(s)')
@click.option('--config', type=click.Path(exists=True),
              help='Load configuration from YAML or JSON file')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--no-warning', is_flag=True,
              help='Skip ethical usage warning (not recommended)')
def scan(target_url: str, depth: int, concurrency: int, follow_subdomains: bool,
         delay_min: float, delay_max: float, no_robots: bool, js_render: bool,
         js_timeout: int, auth_type: Optional[str], auth_user: Optional[str],
         auth_pass: Optional[str], header: tuple, cookie: tuple, timeout: int,
         output: str, formats: tuple, enable_check: tuple, disable_check: tuple,
         config: Optional[str], verbose: bool, no_warning: bool):
    """
    Scan a web application for security vulnerabilities.
    
    TARGET_URL: The starting URL to scan (e.g., https://example.com)
    
    Examples:
    
      Basic scan:
        agri-scanner scan https://example.com
    
      Deep scan with custom settings:
        agri-scanner scan https://example.com -d 3 -c 20 --follow-subdomains
    
      Authenticated scan:
        agri-scanner scan https://example.com --auth-type basic --auth-user admin --auth-pass secret
    
      Custom output and formats:
        agri-scanner scan https://example.com -o ./my-reports -f html -f json -f csv
    """
    # Display ethical warning
    if not no_warning:
        click.echo(ETHICAL_WARNING)
        if not click.confirm('Do you have authorization to scan this target?', default=False):
            click.echo('Scan aborted. Please obtain proper authorization before scanning.')
            sys.exit(1)
    
    # Parse custom headers
    custom_headers = {}
    for h in header:
        if ':' in h:
            key, value = h.split(':', 1)
            custom_headers[key.strip()] = value.strip()
        else:
            click.echo(f"Warning: Invalid header format '{h}', expected 'Name: Value'", err=True)
    
    # Parse custom cookies
    custom_cookies = {}
    for c in cookie:
        if '=' in c:
            key, value = c.split('=', 1)
            custom_cookies[key.strip()] = value.strip()
        else:
            click.echo(f"Warning: Invalid cookie format '{c}', expected 'name=value'", err=True)
    
    # Load configuration from file if provided
    scan_config = None
    if config:
        try:
            scan_config = load_config_file(config)
            click.echo(f"Loaded configuration from {config}")
        except Exception as e:
            click.echo(f"Error loading config file: {e}", err=True)
            sys.exit(1)
    
    # Create or merge configuration
    if scan_config is None:
        scan_config = ScanConfig(target_url=target_url)
    else:
        # CLI arguments override config file
        scan_config.target_url = target_url
    
    # Apply CLI options (override config file)
    scan_config.max_depth = depth
    scan_config.concurrency = concurrency
    scan_config.follow_subdomains = follow_subdomains
    scan_config.delay_min = delay_min
    scan_config.delay_max = delay_max
    scan_config.respect_robots = not no_robots
    scan_config.js_render = js_render
    scan_config.js_timeout = js_timeout
    scan_config.auth_type = auth_type
    scan_config.auth_user = auth_user
    scan_config.auth_pass = auth_pass
    scan_config.timeout = timeout
    scan_config.output_dir = output
    scan_config.report_formats = list(formats)
    scan_config.verbose = verbose
    
    if custom_headers:
        scan_config.custom_headers.update(custom_headers)
    if custom_cookies:
        scan_config.custom_cookies.update(custom_cookies)
    if enable_check:
        scan_config.enabled_checks = list(enable_check)
    if disable_check:
        scan_config.disabled_checks = list(disable_check)
    
    # Validate configuration
    if not scan_config.target_url:
        click.echo("Error: TARGET_URL is required", err=True)
        sys.exit(1)
    
    if not scan_config.target_url.startswith(('http://', 'https://')):
        click.echo("Error: TARGET_URL must start with http:// or https://", err=True)
        sys.exit(1)
    
    # Run the scanner
    try:
        scanner = Scanner(scan_config)
        asyncio.run(scanner.run())
    except KeyboardInterrupt:
        click.echo("\n\nScan interrupted by user.", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n\nFatal error: {e}", err=True)
        logger.exception("Fatal error during scan")
        sys.exit(1)


def load_config_file(filepath: str) -> ScanConfig:
    """
    Load configuration from YAML or JSON file.
    
    Args:
        filepath: Path to configuration file
    
    Returns:
        ScanConfig instance
    
    Raises:
        ValueError: If file format is unsupported or invalid
    """
    import json
    
    path = Path(filepath)
    
    if not path.exists():
        raise ValueError(f"Configuration file not found: {filepath}")
    
    # Read file content
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse based on extension
    if path.suffix in ['.yaml', '.yml']:
        try:
            import yaml
            data = yaml.safe_load(content)
        except ImportError:
            raise ValueError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
        except Exception as e:
            raise ValueError(f"Failed to parse YAML config: {e}")
    elif path.suffix == '.json':
        try:
            data = json.loads(content)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON config: {e}")
    else:
        raise ValueError(f"Unsupported config file format: {path.suffix}. Use .yaml, .yml, or .json")
    
    # Validate required fields
    if 'target_url' not in data:
        data['target_url'] = ""  # Will be overridden by CLI argument
    
    # Create ScanConfig from dictionary
    try:
        return ScanConfig(**data)
    except TypeError as e:
        raise ValueError(f"Invalid configuration: {e}")


if __name__ == '__main__':
    cli()
