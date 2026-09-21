#!/bin/bash
# Stop Dating Agent System

echo ""
echo "Stopping Dating Agent..."
echo ""

# Stop backend
if [ -f .backend.pid ]; then
    PID=$(cat .backend.pid)
    if kill $PID 2>/dev/null; then
        echo "[OK] Stopped backend (PID: $PID)"
    else
        echo "[INFO] Backend already stopped"
    fi
    rm -f .backend.pid
fi

# Fallback: kill by port
if lsof -ti:5001 > /dev/null 2>&1; then
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    echo "[OK] Killed process on port 5001"
fi

echo ""
echo "System stopped."
echo ""
