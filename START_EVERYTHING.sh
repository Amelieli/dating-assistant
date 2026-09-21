#!/bin/bash
# Dating Agent - Complete Startup Script
# Starts backend, frontend, and runs tests

set -e  # Exit on error

echo ""
echo "========================================================================"
echo "          DATING AGENT - COMPLETE SYSTEM STARTUP"
echo "========================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Step 1: Run integration tests
echo "Step 1: Running integration tests..."
echo "--------------------------------------------------------------------"
if python3 test_integration.py; then
    print_status "All integration tests passed!"
else
    print_error "Integration tests failed!"
    exit 1
fi

echo ""
echo "Step 2: Checking dependencies..."
echo "--------------------------------------------------------------------"

# Check if backend deps are installed
print_info "Checking Python dependencies..."
if python3 -c "import flask, flask_cors, requests" 2>/dev/null; then
    print_status "Python dependencies OK"
else
    print_error "Missing Python dependencies. Installing..."
    uv pip install Flask Flask-CORS requests numpy Pillow beautifulsoup4 pydantic python-dotenv
fi

# Check if frontend deps are installed
if [ -d "frontend/node_modules" ]; then
    print_status "Frontend dependencies OK"
else
    print_info "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo ""
echo "Step 3: Starting backend API..."
echo "--------------------------------------------------------------------"

# Start backend in background
cd backend
python3 api.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

print_info "Backend starting on http://localhost:5001 (PID: $BACKEND_PID)"
sleep 3

# Check if backend started successfully
if curl -s http://localhost:5001/health > /dev/null; then
    print_status "Backend API is running!"
else
    print_error "Backend failed to start. Check backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "Step 4: Starting frontend dev server..."
echo "--------------------------------------------------------------------"

# Start frontend in background
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

print_info "Frontend starting on http://localhost:3000 (PID: $FRONTEND_PID)"
sleep 5

if curl -s http://localhost:3000 > /dev/null; then
    print_status "Frontend is running!"
else
    print_error "Frontend failed to start. Check frontend.log"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "========================================================================"
echo "                    SYSTEM READY!"
echo "========================================================================"
echo ""
echo "Services running:"
echo "  - Backend API:    http://localhost:5001"
echo "  - Frontend UI:    http://localhost:3000"
echo ""
echo "Process IDs:"
echo "  - Backend:  $BACKEND_PID"
echo "  - Frontend: $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  - Backend:  backend.log"
echo "  - Frontend: frontend.log"
echo ""
echo "To stop all services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or use:"
echo "  ./STOP_EVERYTHING.sh"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Authenticate with Hinge/Tinder using the UI"
echo "  3. Sync your matches"
echo "  4. Explore the dashboard!"
echo ""
echo "========================================================================"
echo ""

# Save PIDs to file for stopping later
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Wait for user interrupt
echo "Press Ctrl+C to stop all services..."
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f .backend.pid .frontend.pid; echo 'All services stopped.'; exit 0" INT

# Keep script running
wait
