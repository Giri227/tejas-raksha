#!/usr/bin/env python3
"""
================================================================================
🛡️  TEJAS RAKSHA SECURITY SCANNER - INTERACTIVE LAUNCHER
================================================================================
This script provides an interactive interface to run security scans.
Works on Windows, Linux, and macOS.
================================================================================
"""

import os
import sys
import subprocess
import platform
from datetime import datetime


def print_banner():
    """Print the welcome banner."""
    print("\n" + "=" * 80)
    print("🛡️  TEJAS RAKSHA SECURITY SCANNER")
    print("    Protection of Agriculture Web Portals")
    print("=" * 80 + "\n")


def print_step(step_num, total_steps, message):
    """Print a step message."""
    print(f"[{step_num}/{total_steps}] {message}")


def get_target_url():
    """Get target URL from user."""
    print_step(1, 5, "Enter target website URL")
    print("Examples:")
    print("  - http://testphp.vulnweb.com (test site)")
    print("  - https://example.com")
    print("  - http://yourwebsite.com")
    print()
    
    target_url = input("Target URL: ").strip()
    
    if not target_url:
        print("\n✗ No URL provided. Exiting...")
        sys.exit(1)
    
    return target_url


def get_scan_depth():
    """Get scan depth from user."""
    print()
    print_step(2, 5, "Select scan depth")
    print("  1 - Quick Scan (Depth 1, ~2-5 minutes)")
    print("  2 - Normal Scan (Depth 2, ~5-20 minutes)")
    print("  3 - Deep Scan (Depth 3, ~20-60 minutes)")
    print()
    
    choice = input("Enter choice (1/2/3) [default: 1]: ").strip()
    
    if not choice:
        choice = "1"
    
    depth_map = {
        "1": (1, "Quick Scan"),
        "2": (2, "Normal Scan"),
        "3": (3, "Deep Scan")
    }
    
    return depth_map.get(choice, (1, "Quick Scan"))


def get_report_formats():
    """Get report formats from user."""
    print()
    print_step(3, 5, "Select report format(s)")
    print("  1 - HTML only (recommended)")
    print("  2 - HTML + JSON")
    print("  3 - HTML + JSON + CSV (all formats)")
    print()
    
    choice = input("Enter choice (1/2/3) [default: 1]: ").strip()
    
    if not choice:
        choice = "1"
    
    format_map = {
        "1": ["-f", "html"],
        "2": ["-f", "html", "-f", "json"],
        "3": ["-f", "html", "-f", "json", "-f", "csv"]
    }
    
    return format_map.get(choice, ["-f", "html"])


def confirm_scan(target_url, scan_type, depth, output_dir, formats):
    """Display configuration and confirm scan."""
    print()
    print("=" * 80)
    print("SCAN CONFIGURATION")
    print("=" * 80)
    print(f"Target URL:    {target_url}")
    print(f"Scan Type:     {scan_type} (Depth {depth})")
    print(f"Output Dir:    {output_dir}")
    print(f"Report Format: {', '.join([f for f in formats if f != '-f'])}")
    print("=" * 80)
    print()
    
    confirm = input("Start scan? (Y/n): ").strip().lower()
    
    if confirm == "n":
        print("\nScan cancelled.")
        sys.exit(0)


def run_scan(target_url, depth, output_dir, formats):
    """Execute the scan command."""
    print()
    print_step(4, 5, "Starting scan...")
    print()
    print("=" * 80)
    print("⏳ SCANNING IN PROGRESS...")
    print("=" * 80)
    print()
    print("This may take several minutes depending on the scan depth.")
    print("Please wait...")
    print()
    
    # Build command
    cmd = [
        sys.executable, "-m", "src.cli.commands", "scan",
        target_url,
        "--no-warning",
        "-d", str(depth),
        "-o", output_dir,
        *formats,
        "-v"
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    print()
    
    # Run the scan
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n\n✗ Scan interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n✗ Error running scan: {e}")
        return False


def open_report(output_dir):
    """Open the HTML report in the default browser."""
    import glob
    
    html_files = glob.glob(os.path.join(output_dir, "*.html"))
    
    if html_files:
        html_report = html_files[0]
        print(f"\nOpening HTML report: {html_report}")
        
        try:
            if platform.system() == "Windows":
                os.startfile(html_report)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", html_report])
            else:  # Linux
                subprocess.run(["xdg-open", html_report])
        except Exception as e:
            print(f"Could not open report automatically: {e}")
            print(f"Please open manually: {html_report}")


def main():
    """Main function."""
    try:
        # Print banner
        print_banner()
        
        # Get scan parameters
        target_url = get_target_url()
        depth, scan_type = get_scan_depth()
        formats = get_report_formats()
        
        # Generate output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"./scan-results-{timestamp}"
        
        # Confirm scan
        confirm_scan(target_url, scan_type, depth, output_dir, formats)
        
        # Run scan
        success = run_scan(target_url, depth, output_dir, formats)
        
        # Display results
        print()
        print("=" * 80)
        if success:
            print("✓ SCAN COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print()
            print(f"Reports saved to: {output_dir}")
            print()
            
            # Open HTML report
            print_step(5, 5, "Opening report...")
            open_report(output_dir)
            
            print()
            print("Thank you for using Tejas Raksha Security Scanner!")
        else:
            print("✗ SCAN FAILED OR INTERRUPTED")
            print("=" * 80)
            print()
            print("Please check the error messages above.")
        print()
        
    except KeyboardInterrupt:
        print("\n\n✗ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
