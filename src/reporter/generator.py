"""Report generator orchestrator for multiple formats."""

import os
from typing import Dict, List

from ..models.scan_result import ScanResult
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """
    Orchestrates report generation in multiple formats.
    
    Coordinates HTML, JSON, and CSV reporters to generate comprehensive
    security scan reports.
    
    Attributes:
        output_dir: Directory where reports will be saved
    """
    
    def __init__(self, output_dir: str = "./reports"):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory for output reports
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Import reporters (lazy import to avoid circular dependencies)
        from .html_reporter import HTMLReporter
        from .json_reporter import JSONReporter
        from .csv_reporter import CSVReporter
        
        self.html_reporter = HTMLReporter()
        self.json_reporter = JSONReporter()
        self.csv_reporter = CSVReporter()
    
    async def generate_reports(
        self,
        scan_result: ScanResult,
        formats: List[str]
    ) -> Dict[str, str]:
        """
        Generate reports in specified formats.
        
        Args:
            scan_result: Complete scan results
            formats: List of formats to generate ('html', 'json', 'csv', 'all')
        
        Returns:
            Dictionary mapping format to file path
        
        Example:
            >>> generator = ReportGenerator("./reports")
            >>> paths = await generator.generate_reports(result, ['html', 'json'])
            >>> print(paths)
            {'html': './reports/scan_report_20240115_103045.html', 'json': '...'}
        """
        report_paths = {}
        
        # Expand 'all' to all formats
        if 'all' in formats:
            formats = ['html', 'json', 'csv']
        
        logger.info(f"Generating reports in formats: {', '.join(formats)}")
        
        # Generate HTML report
        if 'html' in formats:
            try:
                path = self.html_reporter.generate(scan_result, self.output_dir)
                report_paths['html'] = path
                logger.info(f"HTML report generated: {path}")
            except Exception as e:
                logger.error(f"Failed to generate HTML report: {e}")
        
        # Generate JSON report
        if 'json' in formats:
            try:
                path = self.json_reporter.generate(scan_result, self.output_dir)
                report_paths['json'] = path
                logger.info(f"JSON report generated: {path}")
            except Exception as e:
                logger.error(f"Failed to generate JSON report: {e}")
        
        # Generate CSV report
        if 'csv' in formats:
            try:
                path = self.csv_reporter.generate(scan_result, self.output_dir)
                report_paths['csv'] = path
                logger.info(f"CSV report generated: {path}")
            except Exception as e:
                logger.error(f"Failed to generate CSV report: {e}")
        
        if not report_paths:
            logger.warning("No reports were generated successfully")
        else:
            logger.info(f"Successfully generated {len(report_paths)} report(s)")
        
        return report_paths
    
    def get_output_dir(self) -> str:
        """
        Get the output directory path.
        
        Returns:
            Output directory path
        """
        return self.output_dir
