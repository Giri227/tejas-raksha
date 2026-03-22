@echo off
REM ================================================================================
REM 🛡️  TEJAS RAKSHA SECURITY SCANNER - INTERACTIVE LAUNCHER
REM ================================================================================
REM This script automatically activates the virtual environment and runs a scan
REM ================================================================================

color 0A
cls

echo.
echo ================================================================================
echo 🛡️  TEJAS RAKSHA SECURITY SCANNER
echo     Protection of Agriculture Web Portals
echo ================================================================================
echo.

REM Activate virtual environment
echo [1/5] Activating virtual environment...
call e:\TejasRaksha\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo ✗ Failed to activate virtual environment
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

REM Get target URL
echo [2/5] Enter target website URL
echo Examples:
echo   - http://testphp.vulnweb.com (test site)
echo   - https://example.com
echo   - http://yourwebsite.com
echo.
set /p TARGET_URL="Target URL: "

if "%TARGET_URL%"=="" (
    echo.
    echo ✗ No URL provided. Exiting...
    echo.
    pause
    exit /b 1
)

echo.

REM Get scan depth
echo [3/5] Select scan depth
echo   1 - Quick Scan (Depth 1, ~2-5 minutes)
echo   2 - Normal Scan (Depth 2, ~5-20 minutes)
echo   3 - Deep Scan (Depth 3, ~20-60 minutes)
echo.
set /p DEPTH_CHOICE="Enter choice (1/2/3) [default: 1]: "

if "%DEPTH_CHOICE%"=="" set DEPTH_CHOICE=1

if "%DEPTH_CHOICE%"=="1" (
    set DEPTH=1
    set SCAN_TYPE=Quick Scan
)
if "%DEPTH_CHOICE%"=="2" (
    set DEPTH=2
    set SCAN_TYPE=Normal Scan
)
if "%DEPTH_CHOICE%"=="3" (
    set DEPTH=3
    set SCAN_TYPE=Deep Scan
)

echo.

REM Get report format
echo [4/5] Select report format(s)
echo   1 - HTML only (recommended)
echo   2 - HTML + JSON
echo   3 - HTML + JSON + CSV (all formats)
echo.
set /p FORMAT_CHOICE="Enter choice (1/2/3) [default: 1]: "

if "%FORMAT_CHOICE%"=="" set FORMAT_CHOICE=1

if "%FORMAT_CHOICE%"=="1" set FORMATS=-f html
if "%FORMAT_CHOICE%"=="2" set FORMATS=-f html -f json
if "%FORMAT_CHOICE%"=="3" set FORMATS=-f html -f json -f csv

REM Generate output directory name
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%
set OUTPUT_DIR=./scan-results-%TIMESTAMP%

echo.
echo ================================================================================
echo SCAN CONFIGURATION
echo ================================================================================
echo Target URL:    %TARGET_URL%
echo Scan Type:     %SCAN_TYPE% (Depth %DEPTH%)
echo Output Dir:    %OUTPUT_DIR%
echo Report Format: %FORMATS%
echo ================================================================================
echo.

REM Confirm
set /p CONFIRM="Start scan? (Y/n): "
if /i "%CONFIRM%"=="n" (
    echo.
    echo Scan cancelled.
    echo.
    pause
    exit /b 0
)

echo.
echo [5/5] Starting scan...
echo.
echo ================================================================================
echo ⏳ SCANNING IN PROGRESS...
echo ================================================================================
echo.
echo This may take several minutes depending on the scan depth.
echo Please wait...
echo.

REM Run the scan
python -m src.cli.commands scan "%TARGET_URL%" --no-warning -d %DEPTH% -o "%OUTPUT_DIR%" %FORMATS% -v

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ✗ SCAN FAILED OR INTERRUPTED
    echo ================================================================================
    echo.
    echo Please check the error messages above.
    echo.
) else (
    echo.
    echo ================================================================================
    echo ✓ SCAN COMPLETED SUCCESSFULLY!
    echo ================================================================================
    echo.
    echo Reports saved to: %OUTPUT_DIR%
    echo.
    echo Opening HTML report...
    timeout /t 2 /nobreak >nul
    
    REM Open HTML report
    for %%f in (%OUTPUT_DIR%\*.html) do (
        start "" "%%f"
        goto :report_opened
    )
    :report_opened
    
    echo.
    echo Thank you for using Tejas Raksha Security Scanner!
    echo.
)

pause
