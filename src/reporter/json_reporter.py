"""JSON report generator."""

import json
import os
from datetime import datetime

from ..models.scan_result import ScanResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class JSONReporter:
    """
    Generates JSON reports from scan results.
    
    Creates machine-readable JSON reports with complete finding data,
    scan metadata, and statistics.
    """
    
    def generate(self, scan_result: ScanResult, output_dir: str) -> str:
        """
        Generate JSON report.
        
        Args:
            scan_result: Complete scan results
            output_dir: Directory to save the report
        
        Returns:
            Path to the generated JSON file
        
        Example:
            >>> reporter = JSONReporter()
            >>> path = reporter.generate(scan_result, "./reports")
            >>> print(f"Report saved to {path}")
        """
        # Build report data structure
        report_data = {
            "scan_metadata": self._format_metadata(scan_result.metadata),
            "findings": [self._format_finding(f) for f in scan_result.findings],
            "statistics": scan_result.get_statistics(),
            "errors": scan_result.errors,
        }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scan_report_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
        
        logger.debug(f"JSON report written to {filepath}")
        return filepath
    
    def _format_metadata(self, metadata) -> dict:
        """
        Format scan metadata for JSON output.
        
        Args:
            metadata: ScanMetadata object
        
        Returns:
            Dictionary with formatted metadata
        """
        return {
            "target_url": metadata.target_url,
            "scan_date": metadata.scan_date.isoformat(),
            "duration": round(metadata.duration, 2),
            "pages_crawled": metadata.pages_crawled,
            "pages_discovered": metadata.pages_discovered,
            "scanner_version": metadata.scanner_version,
            "config": metadata.config,
        }
    
    def _format_finding(self, finding) -> dict:
        """
        Format finding for JSON output.
        
        Args:
            finding: Finding object
        
        Returns:
            Dictionary with formatted finding
        """
        return {
            "severity": finding.severity.value,
            "title": finding.title,
            "url": finding.url,
            "description": finding.description,
            "remediation": finding.remediation,
            "category": finding.category,
            "check_name": finding.check_name,
            "timestamp": finding.timestamp.isoformat(),
            "metadata": finding.metadata or {},
        }
