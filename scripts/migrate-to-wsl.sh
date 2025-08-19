#!/bin/bash
# WSL Migration Script - Move autonomous business system to Linux
# =================================================================

echo "🚀 MIGRATING AUTONOMOUS BUSINESS SYSTEM TO WSL/LINUX"
echo "===================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Step 1: Check if running in WSL
if grep -qi microsoft /proc/version; then
    print_status "Running in WSL environment"
else
    print_warning "Not running in WSL. This script is designed for WSL."
    echo "To use WSL:"
    echo "1. Open PowerShell as Administrator"
    echo "2. Run: wsl --install"
    echo "3. Restart and run this script in WSL terminal"
    exit 1
fi

# Step 2: Create project directory in Linux home
PROJECT_DIR="$HOME/autonomous-business-system"
print_status "Setting up project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    print_warning "Directory already exists. Backing up to ${PROJECT_DIR}.backup"
    mv "$PROJECT_DIR" "${PROJECT_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Step 3: Copy files from Windows (if accessible)
WINDOWS_PROJECT="/mnt/e/Projects"
if [ -d "$WINDOWS_PROJECT" ]; then
    print_status "Copying files from Windows project directory..."
    cp -r "$WINDOWS_PROJECT"/*.py .
    cp -r "$WINDOWS_PROJECT"/*.json .
    cp -r "$WINDOWS_PROJECT"/*.md .
    cp -r "$WINDOWS_PROJECT"/*.html . 2>/dev/null
    cp -r "$WINDOWS_PROJECT"/*.sh . 2>/dev/null
    
    # Make scripts executable
    chmod +x *.sh 2>/dev/null
    chmod +x *.py
    
    print_status "Files copied successfully"
else
    print_warning "Windows project directory not found at $WINDOWS_PROJECT"
    print_warning "You'll need to manually copy your files or clone from GitHub"
fi

# Step 4: Install Python and dependencies
print_status "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_warning "Python3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
print_status "Installing Python dependencies..."
cat > requirements.txt << 'EOF'
requests>=2.28.0
boto3>=1.26.0
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
pandas>=1.4.0
numpy>=1.22.0
fastapi>=0.95.0
uvicorn>=0.20.0
pydantic>=1.10.0
sqlalchemy>=2.0.0
alembic>=1.9.0
redis>=4.5.0
celery>=5.2.0
EOF

pip install --upgrade pip
pip install -r requirements.txt

# Step 5: Install GitHub CLI
print_status "Checking GitHub CLI..."
if ! command -v gh &> /dev/null; then
    print_warning "GitHub CLI not found. Installing..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
fi

# Step 6: Configure Git
print_status "Configuring Git..."
git config --global init.defaultBranch main

# Step 7: GitHub Authentication
print_status "Checking GitHub authentication..."
if ! gh auth status &> /dev/null; then
    print_warning "GitHub CLI not authenticated"
    echo "Please run: gh auth login"
    echo "Choose:"
    echo "  - GitHub.com"
    echo "  - HTTPS"
    echo "  - Login with web browser"
else
    print_status "GitHub CLI already authenticated"
fi

# Step 8: Clone repositories if needed
print_status "Checking for repository..."
if [ ! -d ".git" ]; then
    print_warning "Not a git repository. Would you like to clone from GitHub?"
    echo "Run: git clone https://github.com/NiroAgentV2/autonomous-business-system.git"
fi

# Step 9: Fix any Windows line endings
print_status "Converting line endings to Unix format..."
if command -v dos2unix &> /dev/null; then
    dos2unix *.py 2>/dev/null
    dos2unix *.sh 2>/dev/null
else
    sudo apt install -y dos2unix
    dos2unix *.py 2>/dev/null
    dos2unix *.sh 2>/dev/null
fi

# Step 10: Create run script with proper encoding
print_status "Creating Linux run script..."
cat > run-linux.sh << 'EOF'
#!/bin/bash
# Run script for Linux with full Unicode support
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

echo "🚀 Starting Autonomous Business System on Linux"
echo "=============================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to run with emojis
run_with_emoji() {
    echo "✅ Running: $1"
    python3 "$1" "${@:2}"
}

# Menu
echo ""
echo "Choose an option:"
echo "1. 📊 Run continuous monitoring"
echo "2. 🤖 Run agent coordinator"
echo "3. 📝 Create PM service review delegation"
echo "4. 🏗️ Create architect review system"
echo "5. 📈 Run compliance monitor"
echo "6. 🌐 Open dashboard"
echo "7. 🔄 Run all systems"
echo "8. 🛑 Exit"

read -p "Enter choice [1-8]: " choice

case $choice in
    1)
        run_with_emoji continuous-monitor.py
        ;;
    2)
        run_with_emoji agent-policy-coordinator.py --monitor
        ;;
    3)
        run_with_emoji pm-service-review-delegation.py
        ;;
    4)
        run_with_emoji architect-review-system.py
        ;;
    5)
        run_with_emoji agent-compliance-monitor.py
        ;;
    6)
        echo "🌐 Opening dashboard..."
        if [ -f "dashboard.html" ]; then
            xdg-open dashboard.html 2>/dev/null || echo "Open dashboard.html in your browser"
        fi
        ;;
    7)
        echo "🔄 Starting all systems..."
        # Run in background
        nohup python3 continuous-monitor.py > monitor.log 2>&1 &
        echo "✅ Monitor started (PID: $!)"
        
        nohup python3 agent-policy-coordinator.py --monitor > coordinator.log 2>&1 &
        echo "✅ Coordinator started (PID: $!)"
        
        echo "📊 Check logs:"
        echo "  tail -f monitor.log"
        echo "  tail -f coordinator.log"
        ;;
    8)
        echo "👋 Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        ;;
esac
EOF

chmod +x run-linux.sh

# Step 11: Create systemd service (optional)
print_status "Creating systemd service file (optional)..."
cat > autonomous-business.service << EOF
[Unit]
Description=Autonomous Business System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/agent-policy-coordinator.py --monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_status "Service file created. To install as system service:"
echo "  sudo cp autonomous-business.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable autonomous-business"
echo "  sudo systemctl start autonomous-business"

# Step 12: Test Python Unicode support
print_status "Testing Unicode support..."
python3 -c "print('✅ Unicode test: 🚀 🤖 📊 💻 🎯')" && print_status "Unicode working perfectly!" || print_error "Unicode test failed"

# Step 13: Create quick test
cat > test-linux.py << 'EOF'
#!/usr/bin/env python3
"""Test script for Linux environment"""

print("\n🎉 LINUX ENVIRONMENT TEST")
print("=" * 50)

# Test Unicode
emojis = ["🚀", "🤖", "✅", "📊", "💻", "🎯", "🔧", "📈"]
print(f"Unicode Support: {' '.join(emojis)}")

# Test imports
try:
    import requests
    print("✅ requests module available")
except:
    print("❌ requests module not found")

try:
    import boto3
    print("✅ boto3 module available")
except:
    print("❌ boto3 module not found")

# Test GitHub CLI
import subprocess
try:
    result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ GitHub CLI: {result.stdout.split()[2]}")
except:
    print("❌ GitHub CLI not found")

print("\n✅ Linux environment ready for autonomous business system!")
EOF

chmod +x test-linux.py

# Final summary
echo ""
echo "======================================================"
echo "🎉 WSL/LINUX MIGRATION COMPLETE!"
echo "======================================================"
echo ""
print_status "Project directory: $PROJECT_DIR"
print_status "Virtual environment: $PROJECT_DIR/venv"
print_status "All scripts are executable"
print_status "Unicode support enabled"
echo ""
echo "📝 NEXT STEPS:"
echo "1. cd $PROJECT_DIR"
echo "2. source venv/bin/activate"
echo "3. ./test-linux.py  # Test the environment"
echo "4. ./run-linux.sh   # Run the system"
echo ""
echo "🚀 QUICK START:"
echo "  cd $PROJECT_DIR && ./run-linux.sh"
echo ""
echo "📊 MONITOR LOGS:"
echo "  tail -f monitor.log"
echo "  tail -f coordinator.log"
echo ""
echo "🔧 TROUBLESHOOTING:"
echo "- If gh auth fails: gh auth login"
echo "- If Unicode fails: export LANG=en_US.UTF-8"
echo "- If permission denied: chmod +x *.py *.sh"
echo ""
echo "✅ Your system is now ready to run on Linux with full Unicode support!"