# 🐧 WSL Migration Guide for Autonomous Business System

## Quick Migration Steps

### 1. Open WSL Terminal
```bash
# From Windows Terminal or PowerShell:
wsl

# Or open Ubuntu/Debian from Start Menu
```

### 2. Navigate to Windows Project (One-Time Copy)
```bash
# Your Windows E:\Projects is accessible at:
cd /mnt/e/Projects

# Run the migration script:
bash migrate-to-wsl.sh
```

### 3. Or Manual Migration
```bash
# Create Linux project directory
mkdir -p ~/autonomous-business-system
cd ~/autonomous-business-system

# Copy all files from Windows
cp -r /mnt/e/Projects/*.py .
cp -r /mnt/e/Projects/*.json .
cp -r /mnt/e/Projects/*.md .
cp -r /mnt/e/Projects/*.html .
cp -r /mnt/e/Projects/*.sh .

# Make scripts executable
chmod +x *.py *.sh

# Fix line endings
dos2unix *.py *.sh
```

### 4. Install Dependencies
```bash
# Update package manager
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install GitHub CLI
sudo apt install -y gh

# Install dos2unix for line ending conversion
sudo apt install -y dos2unix
```

### 5. Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install Python packages
pip install requests boto3 pytest black flake8
```

### 6. Configure GitHub CLI
```bash
# Authenticate with GitHub
gh auth login

# Choose:
# - GitHub.com
# - HTTPS
# - Login with web browser
```

### 7. Test Unicode Support
```bash
# This should display emojis correctly:
python3 -c "print('🚀 🤖 ✅ 📊 💻')"
```

### 8. Run the System
```bash
# Single run
python3 agent-policy-coordinator.py

# Continuous monitoring
python3 continuous-monitor.py

# Or use the menu
./run-linux.sh
```

## File Access Between Windows and WSL

### From WSL → Windows:
- Windows C: drive → `/mnt/c/`
- Windows E:\Projects → `/mnt/e/Projects/`

### From Windows → WSL:
- WSL home → `\\wsl$\Ubuntu\home\username\`
- In Explorer: `\\wsl$\Ubuntu\home\username\autonomous-business-system\`

## Advantages of Running on WSL/Linux

1. **Full Unicode Support** ✅
   - No more cp1252 encoding errors
   - All emojis work: 🚀 🤖 📊 💻 🎯

2. **Better Performance** 🚀
   - Native Linux filesystem
   - Faster file operations
   - Better process management

3. **Native Tools** 🔧
   - Bash scripting
   - Linux utilities (grep, sed, awk)
   - Better terminal experience

4. **Production-Like Environment** 🏭
   - Same as AWS Lambda/EC2
   - Consistent behavior
   - Easier debugging

## Running as Background Service

### Option 1: Using nohup
```bash
# Start in background
nohup python3 continuous-monitor.py > monitor.log 2>&1 &
nohup python3 agent-policy-coordinator.py > coordinator.log 2>&1 &

# Check logs
tail -f monitor.log
tail -f coordinator.log

# Find process IDs
ps aux | grep python

# Stop services
kill [PID]
```

### Option 2: Using tmux (Recommended)
```bash
# Install tmux
sudo apt install -y tmux

# Create new session
tmux new -s autonomous

# Run your scripts
python3 continuous-monitor.py

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t autonomous
# List sessions: tmux ls
```

### Option 3: Systemd Service
```bash
# Copy service file
sudo cp autonomous-business.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable autonomous-business
sudo systemctl start autonomous-business

# Check status
sudo systemctl status autonomous-business

# View logs
sudo journalctl -u autonomous-business -f
```

## Troubleshooting

### Issue: Permission Denied
```bash
chmod +x *.py *.sh
```

### Issue: Module Not Found
```bash
source venv/bin/activate
pip install [module-name]
```

### Issue: GitHub CLI Not Authenticated
```bash
gh auth login
```

### Issue: Unicode Still Not Working
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export PYTHONIOENCODING=utf-8
```

### Issue: Can't Access Windows Files
```bash
# Check WSL version
wsl --version

# Make sure you're in WSL 2
wsl --set-version Ubuntu 2
```

## VS Code Integration

```bash
# Install VS Code WSL extension
# Then from WSL:
code .

# This opens VS Code connected to WSL
```

## Quick Commands Reference

```bash
# Go to project
cd ~/autonomous-business-system

# Activate Python environment
source venv/bin/activate

# Run monitoring
./run-linux.sh

# Check all logs
tail -f *.log

# See running Python processes
ps aux | grep python

# Kill all Python processes
pkill python3
```

## Migration Complete! 🎉

Your autonomous business system is now running on Linux with:
- ✅ Full Unicode/emoji support
- ✅ Better performance
- ✅ Production-like environment
- ✅ Native Linux tools
- ✅ No encoding errors

The system will work exactly the same but without Windows encoding limitations!