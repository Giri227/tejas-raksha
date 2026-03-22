"""Example: Authenticated scan with custom headers."""

import asyncio
from src.models.config import ScanConfig
from src.scanner import Scanner


async def main():
    """Run an authenticated security scan."""
    
    # Create configuration with authentication
    config = ScanConfig(
        target_url="https://example.com/admin",
        max_depth=2,
        concurrency=5,
        
        # Authentication
        auth_type="basic",
        auth_user="admin",
        auth_pass="password123",
        
        # Custom headers
        custom_headers={
            "X-API-Key": "your-api-key",
            "X-Custom-Header": "value"
        },
        
        # Custom cookies
        custom_cookies={
            "session_id": "abc123xyz",
            "preferences": "dark_mode=true"
        },
        
        # Output settings
        output_dir="./authenticated-reports",
        report_formats=['html', 'json', 'csv'],
        verbose=True
    )
    
    # Run scanner
    scanner = Scanner(config)
    result = await scanner.run()
    
    print(f"\nAuthenticated scan completed!")
    print(f"Total findings: {len(result.findings)}")


if __name__ == '__main__':
    asyncio.run(main())
