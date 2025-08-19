#!/bin/bash

# Quick Local Development Dashboard Setup
echo "🚀 Starting VF Live Dashboard - Local Development Mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "📋 Dashboard Features:"
echo "  ✅ Real-time EC2 monitoring"
echo "  ✅ CloudWatch metrics integration"
echo "  ✅ Cost breakdown by environment"
echo "  ✅ WebSocket live updates"
echo "  ✅ Interactive agent console grid"
echo ""

echo "🔧 Starting dashboard on localhost:5003..."
cd /e/Projects

# Install dependencies if needed
echo "📦 Installing Python dependencies..."
pip install -q flask flask-socketio boto3 psutil

# Start the dashboard
echo "🌐 Dashboard will be available at: http://localhost:5003"
echo "🔄 Auto-refresh: 30 seconds"
echo "☁️ AWS Integration: Live monitoring ready"
echo ""
echo "💡 Next Steps for Production Deployment:"
echo "  1. Configure AWS credentials for VF environments"
echo "  2. Run: ./scripts/deploy-vf-live-dashboard.sh"
echo "  3. Access at: https://dev.visualforge.com/"
echo ""

# Start the dashboard (will run in background)
python vf-dev-live-dashboard.py &

# Get the process ID
DASHBOARD_PID=$!
echo "🎯 Dashboard started with PID: $DASHBOARD_PID"
echo "🛑 To stop: kill $DASHBOARD_PID"
echo ""
echo "📊 Opening dashboard in browser..."

# Wait a moment for server to start
sleep 3

# Try to open in browser (Windows)
if command -v cmd.exe &> /dev/null; then
    cmd.exe /c start http://localhost:5003
elif command -v explorer.exe &> /dev/null; then
    explorer.exe http://localhost:5003
else
    echo "Manual access: http://localhost:5003"
fi

echo "✅ Dashboard is running! Press Ctrl+C to stop."
wait $DASHBOARD_PID
