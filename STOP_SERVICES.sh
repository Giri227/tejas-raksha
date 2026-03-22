#!/bin/bash
################################################################################
# TEJAS RAKSHA DASHBOARD - STOP ALL SERVICES (Linux/Mac)
################################################################################

echo ""
echo "================================================================================"
echo "STOPPING TEJAS RAKSHA DASHBOARD SERVICES"
echo "================================================================================"
echo ""

# Check for PID file
if [ -f "dashboard/backend/.pids" ]; then
    echo "Stopping services using saved PIDs..."
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Killing process $pid"
            kill $pid 2>/dev/null
        fi
    done < dashboard/backend/.pids
    rm -f dashboard/backend/.pids
    echo "[OK] Services stopped"
else
    echo "No PID file found, searching for processes..."
    
    # Kill by process name
    pkill -f 'run_celery.py' 2>/dev/null && echo "[OK] Celery Worker stopped"
    pkill -f 'run_server.py' 2>/dev/null && echo "[OK] FastAPI Server stopped"
fi

# Check port 8000
echo ""
echo "Checking for processes on port 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "[OK] Port 8000 cleared"
else
    echo "[INFO] No processes on port 8000"
fi

echo ""
echo "================================================================================"
echo "ALL SERVICES STOPPED"
echo "================================================================================"
echo ""
