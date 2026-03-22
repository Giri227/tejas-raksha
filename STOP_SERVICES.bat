@echo off
REM ================================================================================
REM TEJAS RAKSHA DASHBOARD - STOP ALL SERVICES
REM ================================================================================

echo.
echo ================================================================================
echo STOPPING TEJAS RAKSHA DASHBOARD SERVICES
echo ================================================================================
echo.

echo Stopping Celery Worker...
taskkill /FI "WINDOWTITLE eq Tejas Raksha - Celery Worker*" /F >nul 2>&1
if errorlevel 1 (
    echo [INFO] Celery Worker window not found
) else (
    echo [OK] Celery Worker stopped
)

echo Stopping FastAPI Server...
taskkill /FI "WINDOWTITLE eq Tejas Raksha - FastAPI Server*" /F >nul 2>&1
if errorlevel 1 (
    echo [INFO] FastAPI Server window not found
) else (
    echo [OK] FastAPI Server stopped
)

echo.
echo Checking for processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo ================================================================================
echo ALL SERVICES STOPPED
echo ================================================================================
echo.
pause
