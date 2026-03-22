"""HTML report generator with embedded CSS, JavaScript, and logo."""

import os
import base64
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..models.scan_result import ScanResult
from ..models.finding import Severity
from ..utils.logger import get_logger

logger = get_logger(__name__)


class HTMLReporter:
    """
    Generates interactive HTML reports from scan results.
    
    Creates comprehensive HTML reports with embedded CSS, JavaScript, and logo,
    severity charts, filtering capabilities, and responsive design.
    """
    
    def __init__(self):
        """Initialize HTML reporter with Jinja2 environment."""
        # Get the directory containing this file
        current_dir = Path(__file__).parent
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(current_dir / 'templates')),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Load static files
        self.css_content = self._load_static_file('styles.css')
        self.js_content = self._load_static_file('scripts.js')
        self.logo_base64 = self._load_logo()
    
    def _load_static_file(self, filename: str) -> str:
        """
        Load content from static file.
        
        Args:
            filename: Name of the file in static directory
        
        Returns:
            File content as string
        """
        current_dir = Path(__file__).parent
        static_path = current_dir / 'static' / filename
        
        try:
            with open(static_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load static file {filename}: {e}")
            return ""
    
    def _load_logo(self) -> str:
        """
        Load and encode logo as base64.
        
        Returns:
            Base64 encoded logo string, or empty string if not found
        """
        # Try multiple possible logo locations
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / 'logo' / 'tejesRaskalogo.png',
            Path.cwd() / 'logo' / 'tejesRaskalogo.png',
            Path(__file__).parent / 'static' / 'logo.png',
        ]
        
        for logo_path in possible_paths:
            if logo_path.exists():
                try:
                    with open(logo_path, 'rb') as f:
                        logo_data = f.read()
                        logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                        logger.debug(f"Logo loaded from {logo_path}")
                        return logo_base64
                except Exception as e:
                    logger.warning(f"Failed to load logo from {logo_path}: {e}")
        
        logger.warning("Logo not found in any expected location")
        return ""
    
    def generate(self, scan_result: ScanResult, output_dir: str) -> str:
        """
        Generate HTML report.
        
        Args:
            scan_result: Complete scan results
            output_dir: Directory to save the report
        
        Returns:
            Path to the generated HTML file
        
        Example:
            >>> reporter = HTMLReporter()
            >>> path = reporter.generate(scan_result, "./reports")
            >>> print(f"Report saved to {path}")
        """
        # Group findings by severity
        findings_by_severity = self._group_findings_by_severity(scan_result)
        
        # Prepare template context
        context = {
            'scan_metadata': self._format_metadata(scan_result.metadata),
            'findings': scan_result.findings,
            'findings_by_severity': findings_by_severity,
            'statistics': scan_result.get_statistics(),
            'embedded_css': self.css_content,
            'embedded_js': self.js_content,
            'logo_base64': self.logo_base64,
        }
        
        # Load and render template
        template = self.env.get_template('report.html.j2')
        html_content = template.render(**context)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scan_report_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        # Write HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.debug(f"HTML report written to {filepath}")
        return filepath
    
    def _format_metadata(self, metadata) -> dict:
        """
        Format scan metadata for template rendering.
        
        Args:
            metadata: ScanMetadata object
        
        Returns:
            Dictionary with formatted metadata
        """
        return {
            'target_url': metadata.target_url,
            'scan_date': metadata.scan_date.strftime("%Y-%m-%d %H:%M:%S"),
            'duration': round(metadata.duration, 2),
            'pages_crawled': metadata.pages_crawled,
            'pages_discovered': metadata.pages_discovered,
            'scanner_version': metadata.scanner_version,
        }
    
    def _group_findings_by_severity(self, scan_result: ScanResult) -> dict:
        """
        Group findings by severity level for summary display.
        
        Args:
            scan_result: Complete scan results
        
        Returns:
            Dictionary mapping severity names to lists of findings
        """
        grouped = {
            'High': [],
            'Medium': [],
            'Low': [],
            'Info': [],
        }
        
        for finding in scan_result.findings:
            severity_name = finding.severity.value
            if severity_name in grouped:
                grouped[severity_name].append(finding)
        
        return grouped
