"""Data models for scan results and metadata."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from .finding import Finding, Severity


@dataclass
class ScanMetadata:
    """
    Metadata about a security scan.
    
    Attributes:
        target_url: The starting URL that was scanned
        scan_date: When the scan was initiated
        duration: Total scan duration in seconds
        pages_crawled: Number of pages successfully crawled
        pages_discovered: Total number of unique URLs discovered
        scanner_version: Version of the scanner software
        config: Configuration parameters used for the scan
    """
    
    target_url: str
    scan_date: datetime
    duration: float
    pages_crawled: int
    pages_discovered: int
    scanner_version: str
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'target_url': self.target_url,
            'scan_date': self.scan_date.isoformat(),
            'duration': round(self.duration, 2),
            'pages_crawled': self.pages_crawled,
            'pages_discovered': self.pages_discovered,
            'scanner_version': self.scanner_version,
            'config': self.config,
        }


@dataclass
class ScanResult:
    """
    Complete results from a security scan.
    
    Attributes:
        metadata: Scan metadata and configuration
        findings: List of security findings discovered
        errors: List of error messages encountered during scan
    """
    
    metadata: ScanMetadata
    findings: List[Finding] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def get_findings_by_severity(self) -> Dict[Severity, List[Finding]]:
        """
        Group findings by severity level.
        
        Returns:
            Dictionary mapping severity levels to lists of findings
        """
        grouped: Dict[Severity, List[Finding]] = {severity: [] for severity in Severity}
        for finding in self.findings:
            grouped[finding.severity].append(finding)
        return grouped
    
    def get_findings_by_category(self) -> Dict[str, List[Finding]]:
        """
        Group findings by category.
        
        Returns:
            Dictionary mapping categories to lists of findings
        """
        grouped: Dict[str, List[Finding]] = {}
        for finding in self.findings:
            if finding.category not in grouped:
                grouped[finding.category] = []
            grouped[finding.category].append(finding)
        return grouped
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate scan statistics.
        
        Returns:
            Dictionary containing various statistics about the scan
        """
        by_severity = self.get_findings_by_severity()
        by_category = self.get_findings_by_category()
        
        # Calculate pages per minute
        pages_per_minute = 0.0
        if self.metadata.duration > 0:
            pages_per_minute = (self.metadata.pages_crawled / self.metadata.duration) * 60
        
        return {
            'total_findings': len(self.findings),
            'by_severity': {
                severity.value: len(findings)
                for severity, findings in by_severity.items()
            },
            'by_category': {
                category: len(findings)
                for category, findings in by_category.items()
            },
            'pages_per_minute': round(pages_per_minute, 2),
            'error_count': len(self.errors),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scan result to dictionary."""
        return {
            'metadata': self.metadata.to_dict(),
            'findings': [f.to_dict() for f in self.findings],
            'errors': self.errors,
            'statistics': self.get_statistics(),
        }
