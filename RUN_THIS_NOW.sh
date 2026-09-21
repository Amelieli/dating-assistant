#!/bin/bash
# Quick test and demo script for the dating agent

echo "==========================================="
echo "DATING AGENT - QUICK TEST"
echo "==========================================="
echo ""

# Test 1: Run integration tests
echo "Step 1: Running integration tests..."
python3 test_integration.py

if [ $? -eq 0 ]; then
    echo ""
    echo "==========================================="
    echo "SUCCESS! All systems operational"
    echo "==========================================="
    echo ""
    echo "What you can do now:"
    echo ""
    echo "1. Test with mock data:"
    echo "   python3 -c 'from dating_agent.profile_aggregator import profile_aggregator; agg = profile_aggregator(); print(\"Ready!\")'"
    echo ""
    echo "2. Start the backend API:"
    echo "   cd backend && python3 api.py"
    echo "   # Then visit: http://localhost:5000/health"
    echo ""
    echo "3. Run Hinge quick start (needs credentials):"
    echo "   python3 quick_start_hinge.py"
    echo ""
    echo "4. Run Tinder quick start (needs credentials):"
    echo "   python3 quick_start_tinder.py"
    echo ""
    echo "5. Check the status docs:"
    echo "   cat INTEGRATION_COMPLETE.md"
    echo "   cat CURRENT_STATUS_JAN_2026.md"
    echo ""
else
    echo ""
    echo "==========================================="
    echo "Tests failed! Check output above"
    echo "==========================================="
    exit 1
fi
