"""Main scanner controller orchestrating the complete scan workflow."""

import asyncio
import os
import time
from datetime import datetime
from typing import List

from .models.config import ScanConfig
from .models.finding import Finding
from .models.scan_result import ScanResult, ScanMetadata
from .crawler.controller import CrawlerController
from .checks.registry import CheckRegistry
from .reporter.generator import ReportGenerator
from .utils.logger import get_logger

logger = get_logger(__name__)

SCANNER_VERSION = "1.0.0"


class Scanner:
    """
    Main scanner orchestrator.
    
    Coordinates the complete security scan workflow:
    1. Crawl phase - Discover URLs
    2. Check phase - Execute security checks
    3. Report phase - Generate reports
    
    Attributes:
        config: Scan configuration
    """
    
    def __init__(self, config: ScanConfig):
        """
        Initialize scanner with configuration.
        
        Args:
            config: Complete scan configuration
        """
        self.config = config
        self.start_time = 0.0
        self.end_time = 0.0
        
        # Initialize components
        self.crawler = None
        self.check_registry = None
        self.report_generator = None
    
    async def run(self) -> ScanResult:
        """
        Execute complete scan workflow.
        
        Returns:
            Complete scan results
        
        Raises:
            Exception: If any critical error occurs during scan
        """
        self.start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("🛡️  Tejas Raksha Security Scanner v%s", SCANNER_VERSION)
        logger.info("=" * 80)
        logger.info("Target: %s", self.config.target_url)
        logger.info("Max Depth: %d", self.config.max_depth)
        logger.info("Concurrency: %d", self.config.concurrency)
        logger.info("=" * 80)
        
        # Phase 1: Crawl
        discovered_urls = await self._crawl_phase()
        
        # Phase 2: Security Checks
        findings = await self._check_phase(discovered_urls)
        
        # Phase 3: Generate Reports
        scan_result = self._create_scan_result(discovered_urls, findings)
        report_paths = await self._report_phase(scan_result)
        
        # Display summary
        self._display_summary(scan_result, report_paths)
        
        self.end_time = time.time()
        logger.info("Scan completed in %.2f seconds", self.end_time - self.start_time)
        
        return scan_result
    
    async def _crawl_phase(self) -> List[str]:
        """
        Phase 1: Crawl target and discover URLs.
        
        Returns:
            List of discovered URLs
        """
        logger.info("\n" + "=" * 80)
        logger.info("📡 PHASE 1: CRAWLING")
        logger.info("=" * 80)
        
        try:
            # Import crawler components
            from .crawler.fetcher import Fetcher
            from .crawler.parser import Parser
            from .crawler.frontier import Frontier
            from .utils.rate_limiter import RateLimiter
            from .utils.robots_parser import RobotsParser
            
            # Initialize components
            rate_limiter = RateLimiter(
                min_delay=self.config.delay_min,
                max_delay=self.config.delay_max
            )
            
            robots_parser = RobotsParser()
            
            # Prepare auth tuple if credentials provided
            auth = None
            if self.config.auth_user and self.config.auth_pass:
                auth = (self.config.auth_user, self.config.auth_pass)
            
            fetcher = Fetcher(
                rate_limiter=rate_limiter,
                robots_parser=robots_parser,
                user_agents=self.config.user_agents,
                timeout=self.config.timeout,
                auth=auth,
                custom_headers=self.config.custom_headers,
                custom_cookies=self.config.custom_cookies
            )
            
            parser = Parser(base_url=self.config.target_url)
            frontier = Frontier()
            
            self.crawler = CrawlerController(
                fetcher=fetcher,
                parser=parser,
                frontier=frontier,
                target_url=self.config.target_url,
                max_depth=self.config.max_depth,
                follow_subdomains=self.config.follow_subdomains,
                concurrency=self.config.concurrency
            )
            
            discovered_urls = await self.crawler.crawl(self.config.target_url)
            
            logger.info("✓ Crawling complete")
            logger.info("  • Pages discovered: %d", len(discovered_urls))
            logger.info("  • Pages crawled: %d", self.crawler.get_stats()['pages_crawled'])
            
            return list(discovered_urls)
            
        except Exception as e:
            logger.error("✗ Crawling failed: %s", e)
            logger.exception("Crawl phase error")
            # Return empty list to allow scan to continue
            return []
    
    async def _check_phase(self, discovered_urls: List[str]) -> List[Finding]:
        """
        Phase 2: Execute security checks on discovered URLs.
        
        Args:
            discovered_urls: List of URLs to check
        
        Returns:
            List of security findings
        """
        logger.info("\n" + "=" * 80)
        logger.info("🔍 PHASE 2: SECURITY CHECKS")
        logger.info("=" * 80)
        
        if not discovered_urls:
            logger.warning("No URLs to check. Skipping security checks.")
            return []
        
        try:
            # Import check components
            from .checks.registry import CheckRegistry
            from .checks.base import CheckContext
            from .crawler.fetcher import Fetcher
            from .utils.rate_limiter import RateLimiter
            from .utils.robots_parser import RobotsParser
            
            # Create fetcher for checks
            rate_limiter = RateLimiter(
                min_delay=self.config.delay_min,
                max_delay=self.config.delay_max
            )
            
            robots_parser = RobotsParser()
            
            # Prepare auth tuple if credentials provided
            auth = None
            if self.config.auth_user and self.config.auth_pass:
                auth = (self.config.auth_user, self.config.auth_pass)
            
            fetcher = Fetcher(
                rate_limiter=rate_limiter,
                robots_parser=robots_parser,
                user_agents=self.config.user_agents,
                timeout=self.config.timeout,
                auth=auth,
                custom_headers=self.config.custom_headers,
                custom_cookies=self.config.custom_cookies
            )
            
            # Create check context
            context = CheckContext(
                urls=set(discovered_urls),
                fetcher=fetcher,
                config=self.config,
                scan_metadata={
                    'target_url': self.config.target_url,
                    'start_time': self.start_time,
                }
            )
            
            # Initialize and execute checks
            self.check_registry = CheckRegistry(self.config)
            self.check_registry.discover_checks()
            
            if self.check_registry.get_check_count() == 0:
                logger.warning("No security checks discovered")
                return []
            
            findings = await self.check_registry.execute_all(context)
            
            logger.info("✓ Security checks complete")
            logger.info("  • Total findings: %d", len(findings))
            
            # Count by severity
            severity_counts = {}
            for finding in findings:
                severity = finding.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for severity, count in sorted(severity_counts.items()):
                logger.info("  • %s: %d", severity, count)
            
            return findings
            
        except Exception as e:
            logger.error("✗ Security checks failed: %s", e)
            logger.exception("Check phase error")
            # Return empty list to allow scan to continue
            return []
    
    async def _report_phase(self, scan_result: ScanResult) -> dict:
        """
        Phase 3: Generate reports in configured formats.
        
        Args:
            scan_result: Complete scan results
        
        Returns:
            Dictionary mapping format to file path
        """
        logger.info("\n" + "=" * 80)
        logger.info("📊 PHASE 3: REPORT GENERATION")
        logger.info("=" * 80)
        
        try:
            # Create output directory
            os.makedirs(self.config.output_dir, exist_ok=True)
            
            self.report_generator = ReportGenerator(self.config.output_dir)
            report_paths = await self.report_generator.generate_reports(
                scan_result,
                self.config.report_formats
            )
            
            logger.info("✓ Report generation complete")
            for format_name, path in report_paths.items():
                logger.info("  • %s: %s", format_name.upper(), path)
            
            return report_paths
            
        except Exception as e:
            logger.error("✗ Report generation failed: %s", e)
            logger.exception("Report phase error")
            return {}
    
    def _create_scan_result(self, discovered_urls: List[str], findings: List[Finding]) -> ScanResult:
        """
        Create ScanResult object with metadata.
        
        Args:
            discovered_urls: List of discovered URLs
            findings: List of security findings
        
        Returns:
            Complete scan result
        """
        duration = time.time() - self.start_time
        
        # Get crawl statistics
        pages_crawled = 0
        if self.crawler:
            stats = self.crawler.get_stats()
            pages_crawled = stats.get('pages_crawled', 0)
        
        metadata = ScanMetadata(
            target_url=self.config.target_url,
            scan_date=datetime.now(),
            duration=duration,
            pages_crawled=pages_crawled,
            pages_discovered=len(discovered_urls),
            scanner_version=SCANNER_VERSION,
            config=self.config.to_dict()
        )
        
        return ScanResult(
            metadata=metadata,
            findings=findings,
            errors=[]
        )
    
    def _display_summary(self, scan_result: ScanResult, report_paths: dict) -> None:
        """
        Display final scan summary to console.
        
        Args:
            scan_result: Complete scan results
            report_paths: Dictionary of generated report paths
        """
        logger.info("\n" + "=" * 80)
        logger.info("📋 SCAN SUMMARY")
        logger.info("=" * 80)
        
        stats = scan_result.get_statistics()
        
        # Display findings by severity with color coding
        logger.info("\nFindings by Severity:")
        severity_colors = {
            'High': '\033[91m',    # Red
            'Medium': '\033[93m',  # Yellow
            'Low': '\033[94m',     # Blue
            'Info': '\033[90m'     # Gray
        }
        reset_color = '\033[0m'
        
        for severity in ['High', 'Medium', 'Low', 'Info']:
            count = stats['by_severity'].get(severity, 0)
            color = severity_colors.get(severity, '')
            logger.info("  %s• %s: %d%s", color, severity, count, reset_color)
        
        logger.info("\nScan Performance:")
        logger.info("  • Duration: %.2f seconds", scan_result.metadata.duration)
        logger.info("  • Pages crawled: %d", scan_result.metadata.pages_crawled)
        logger.info("  • Pages discovered: %d", scan_result.metadata.pages_discovered)
        logger.info("  • Throughput: %.2f pages/minute", stats['pages_per_minute'])
        
        if report_paths:
            logger.info("\nGenerated Reports:")
            for format_name, path in report_paths.items():
                logger.info("  • %s: %s", format_name.upper(), path)
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ Scan complete!")
        logger.info("=" * 80)
