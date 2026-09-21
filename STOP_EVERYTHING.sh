#!/bin/bash
# Stop all Dating Agent services

echo "Stopping Dating Agent services..."

# Read PIDs from files
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo "  Stopped backend (PID: $BACKEND_PID)" || echo "  Backend already stopped"
    rm -f .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo "  Stopped frontend (PID: $FRONTEND_PID)" || echo "  Frontend already stopped"
    rm -f .frontend.pid
fi

# Fallback: kill by port
lsof -ti:5001 | xargs kill 2>/dev/null && echo "  Killed process on port 5001" || true
lsof -ti:3000 | xargs kill 2>/dev/null && echo "  Killed process on port 3000" || true

echo "All services stopped."
