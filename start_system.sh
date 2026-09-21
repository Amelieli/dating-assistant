#!/bin/bash
# Complete Dating Agent Startup Script

echo ""
echo "========================================================================"
echo "            DATING AGENT - COMPLETE STARTUP"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[OK]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# Step 1: Check if backend is already running
echo "Step 1: Checking existing backend..."
if lsof -ti:5001 > /dev/null 2>&1; then
    print_info "Backend already running on port 5001"
    echo "  Stopping old instance..."
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    sleep 1
fi
print_status "Port 5001 is free"
echo ""

# Step 2: Start backend
echo "Step 2: Starting backend..."
cd backend
python3 api.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo $BACKEND_PID > .backend.pid
print_info "Backend starting (PID: $BACKEND_PID)"
sleep 3
echo ""

# Step 3: Test backend
echo "Step 3: Testing backend..."
if curl -s http://localhost:5001/health > /dev/null 2>&1; then
    print_status "Backend is responding!"
else
    print_error "Backend failed to start"
    echo "Check backend.log for errors:"
    tail -10 backend.log
    exit 1
fi
echo ""

# Step 4: Initialize orchestrator
echo "Step 4: Initializing orchestrator..."
INIT_RESPONSE=$(curl -s -X POST http://localhost:5001/init \
  -H "Content-Type: application/json" \
  -d '{
    "min_age": 18,
    "max_age": 100,
    "max_distance_km": 50,
    "use_clip": true
  }')

if echo "$INIT_RESPONSE" | grep -q "initialized"; then
    print_status "Orchestrator initialized!"
else
    print_info "Orchestrator may already be initialized"
fi
echo ""

# Step 5: Verify all endpoints
echo "Step 5: Verifying endpoints..."
curl -s http://localhost:5001/stats > /dev/null && print_status "/stats working"
curl -s http://localhost:5001/matches/mutual > /dev/null && print_status "/matches/mutual working"
curl -s http://localhost:5001/health > /dev/null && print_status "/health working"
echo ""

# Step 6: Show status
echo "========================================================================"
echo "                    SYSTEM READY!"
echo "========================================================================"
echo ""
echo "Backend:     http://localhost:5001        [RUNNING]"
echo "UI:          http://localhost:5001        [DARK THEME]"
echo "Backend PID: $BACKEND_PID"
echo "Log file:    backend.log"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID"
echo "  # Or run: ./stop_system.sh"
echo ""
echo "To view logs:"
echo "  tail -f backend.log"
echo ""
echo "Next steps:"
echo "  1. Open: http://localhost:5001"
echo "  2. Get X-Auth-Token from Tinder (see GET_REAL_TINDER_TOKEN.md)"
echo "  3. Sync profiles!"
echo ""
echo "========================================================================"
echo ""
