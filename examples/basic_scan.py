"""Example: Basic programmatic usage of the scanner."""

import asyncio
from src.models.config import ScanConfig
from src.scanner import Scanner


async def main():
    """Run a basic security scan programmatically."""
    
    # Create configuration
    config = ScanConfig(
        target_url="https://example.com",
        max_depth=2,
        concurrency=10,
        output_dir="./example-reports",
        report_formats=['html', 'json'],
        verbose=True
    )
    
    # Create and run scanner
    scanner = Scanner(config)
    result = await scanner.run()
    
    # Access results
    print(f"\nScan completed!")
    print(f"Total findings: {len(result.findings)}")
    print(f"Pages crawled: {result.metadata.pages_crawled}")
    print(f"Duration: {result.metadata.duration:.2f} seconds")
    
    # Print findings by severity
    by_severity = result.get_findings_by_severity()
    for severity, findings in by_severity.items():
        if findings:
            print(f"\n{severity.value} severity: {len(findings)} findings")
            for finding in findings[:3]:  # Show first 3
                print(f"  - {finding.title}")


if __name__ == '__main__':
    asyncio.run(main())
