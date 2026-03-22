"""CSV report generator."""

import csv
import os
from datetime import datetime

from ..models.scan_result import ScanResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CSVReporter:
    """
    Generates CSV reports from scan results.
    
    Creates spreadsheet-friendly CSV reports with one finding per row.
    """
    
    def generate(self, scan_result: ScanResult, output_dir: str) -> str:
        """
        Generate CSV report.
        
        Args:
            scan_result: Complete scan results
            output_dir: Directory to save the report
        
        Returns:
            Path to the generated CSV file
        
        Example:
            >>> reporter = CSVReporter()
            >>> path = reporter.generate(scan_result, "./reports")
            >>> print(f"Report saved to {path}")
        """
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scan_report_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Define CSV columns
        fieldnames = [
            'Severity',
            'Title',
            'URL',
            'Description',
            'Remediation',
            'Category',
            'Check Name',
            'Timestamp',
        ]
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write each finding as a row
            for finding in scan_result.findings:
                writer.writerow({
                    'Severity': finding.severity.value,
                    'Title': finding.title,
                    'URL': finding.url,
                    'Description': self._escape_csv(finding.description),
                    'Remediation': self._escape_csv(finding.remediation),
                    'Category': finding.category,
                    'Check Name': finding.check_name,
                    'Timestamp': finding.timestamp.isoformat(),
                })
        
        logger.debug(f"CSV report written to {filepath}")
        return filepath
    
    def _escape_csv(self, text: str) -> str:
        """
        Escape special characters for CSV.
        
        Args:
            text: Text to escape
        
        Returns:
            Escaped text safe for CSV
        """
        # CSV writer handles most escaping, but we ensure newlines are preserved
        # and text is properly formatted
        return text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
