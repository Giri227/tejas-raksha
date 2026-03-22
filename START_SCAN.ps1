# ================================================================================
# 🛡️  TEJAS RAKSHA SECURITY SCANNER - INTERACTIVE LAUNCHER
# ================================================================================
# This script automatically activates the virtual environment and runs a scan
# ================================================================================

# Set colors
$Host.UI.RawUI.BackgroundColor = "Black"
Clear-Host

# Banner
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🛡️  TEJAS RAKSHA SECURITY SCANNER" -ForegroundColor Green
Write-Host "    Protection of Agriculture Web Portals" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "[1/5] Activating virtual environment..." -ForegroundColor Yellow
$venvPath = "e:/TejasRaksha/.venv/Scripts/Activate.ps1"

if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found at: $venvPath" -ForegroundColor Red
    Write-Host "Please check the path and try again." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Get target URL
Write-Host "[2/5] Enter target website URL" -ForegroundColor Yellow
Write-Host "Examples:" -ForegroundColor Gray
Write-Host "  - http://testphp.vulnweb.com (test site)" -ForegroundColor Gray
Write-Host "  - https://example.com" -ForegroundColor Gray
Write-Host "  - http://yourwebsite.com" -ForegroundColor Gray
Write-Host ""
$targetUrl = Read-Host "Target URL"

if ([string]::IsNullOrWhiteSpace($targetUrl)) {
    Write-Host ""
    Write-Host "✗ No URL provided. Exiting..." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Get scan depth
Write-Host "[3/5] Select scan depth" -ForegroundColor Yellow
Write-Host "  1 - Quick Scan (Depth 1, ~2-5 minutes)" -ForegroundColor White
Write-Host "  2 - Normal Scan (Depth 2, ~5-20 minutes)" -ForegroundColor White
Write-Host "  3 - Deep Scan (Depth 3, ~20-60 minutes)" -ForegroundColor White
Write-Host ""
$depthChoice = Read-Host "Enter choice (1/2/3) [default: 1]"

if ([string]::IsNullOrWhiteSpace($depthChoice)) {
    $depthChoice = "1"
}

switch ($depthChoice) {
    "1" { $depth = 1; $scanType = "Quick Scan" }
    "2" { $depth = 2; $scanType = "Normal Scan" }
    "3" { $depth = 3; $scanType = "Deep Scan" }
    default { $depth = 1; $scanType = "Quick Scan" }
}

Write-Host ""

# Get report format
Write-Host "[4/5] Select report format(s)" -ForegroundColor Yellow
Write-Host "  1 - HTML only (recommended)" -ForegroundColor White
Write-Host "  2 - HTML + JSON" -ForegroundColor White
Write-Host "  3 - HTML + JSON + CSV (all formats)" -ForegroundColor White
Write-Host ""
$formatChoice = Read-Host "Enter choice (1/2/3) [default: 1]"

if ([string]::IsNullOrWhiteSpace($formatChoice)) {
    $formatChoice = "1"
}

switch ($formatChoice) {
    "1" { $formats = "-f html" }
    "2" { $formats = "-f html -f json" }
    "3" { $formats = "-f html -f json -f csv" }
    default { $formats = "-f html" }
}

# Generate output directory name
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputDir = "./scan-results-$timestamp"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "SCAN CONFIGURATION" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Target URL:    $targetUrl" -ForegroundColor White
Write-Host "Scan Type:     $scanType (Depth $depth)" -ForegroundColor White
Write-Host "Output Dir:    $outputDir" -ForegroundColor White
Write-Host "Report Format: $($formats -replace '-f ', '')" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Confirm
$confirm = Read-Host "Start scan? (Y/n)"
if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host ""
    Write-Host "Scan cancelled." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "[5/5] Starting scan..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "⏳ SCANNING IN PROGRESS..." -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This may take several minutes depending on the scan depth." -ForegroundColor Gray
Write-Host "Please wait..." -ForegroundColor Gray
Write-Host ""

# Build and execute command
$command = "python -m src.cli.commands scan `"$targetUrl`" --no-warning -d $depth -o `"$outputDir`" $formats -v"

Write-Host "Executing: $command" -ForegroundColor Gray
Write-Host ""

# Run the scan
Invoke-Expression $command

# Check if scan completed
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "✓ SCAN COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Reports saved to: $outputDir" -ForegroundColor White
    Write-Host ""
    
    # Find and open HTML report
    $htmlReport = Get-ChildItem -Path $outputDir -Filter "*.html" | Select-Object -First 1
    if ($htmlReport) {
        Write-Host "Opening HTML report..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        Invoke-Item $htmlReport.FullName
    }
    
    Write-Host ""
    Write-Host "Thank you for using Tejas Raksha Security Scanner!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "✗ SCAN FAILED OR INTERRUPTED" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to exit"
