# 🚀 HOW TO RUN DEV AGENTS WITH COST PROTECTION

## 🎯 **QUICK START (RECOMMENDED)**

### **Option 1: Simple Dev Launcher** ⭐
```bash
# Easy way - starts everything for you
E:/Projects/.venv/Scripts/python.exe E:/Projects/simple-dev-launcher.py
```

### **Option 2: Manual Individual Agents**
```bash
# Terminal 1: Start cost monitoring
E:/Projects/.venv/Scripts/python.exe E:/Projects/aws-cost-monitor.py --threshold 3.0 --window 30

# Terminal 2: Start service monitoring
E:/Projects/.venv/Scripts/python.exe E:/Projects/monitorable-agent.py

# Terminal 3: Start log monitoring  
E:/Projects/.venv/Scripts/python.exe E:/Projects/log-monitor.py

# Terminal 4: View dashboard
E:/Projects/.venv/Scripts/python.exe E:/Projects/dev-failsafe-dashboard.py
```

### **Option 3: Full Orchestrator** (Advanced)
```bash
# Complete orchestrator with auto-restart
E:/Projects/.venv/Scripts/python.exe E:/Projects/dev-focused-orchestrator.py
```

## 📊 **VIEW STATUS & LOGS**

### **Check Current Status**
```bash
E:/Projects/.venv/Scripts/python.exe E:/Projects/dev-focused-orchestrator.py --status
```

### **View Real-time Dashboard**
```bash
E:/Projects/.venv/Scripts/python.exe E:/Projects/dev-failsafe-dashboard.py
```

### **View Logs**
```bash
# View agent logs
E:/Projects/.venv/Scripts/python.exe E:/Projects/log-monitor.py

# Check log files directly
cat E:/Projects/agent_logs/agent.log
cat E:/Projects/agent_logs/aws_cost_monitor.log
```

## 🛑 **STOP EVERYTHING**

### **Stop All Agents**
```bash
E:/Projects/.venv/Scripts/python.exe E:/Projects/dev-focused-orchestrator.py --stop
```

### **Emergency Kill All**
```bash
# Windows
taskkill /f /im python.exe

# Or use PowerShell
powershell "Stop-Process -Name python -Force"
```

## 🔧 **TROUBLESHOOTING**

### **If Agents Keep Failing**
1. **Check Dependencies**:
   ```bash
   E:/Projects/.venv/Scripts/pip install boto3 psutil requests
   ```

2. **Check AWS Credentials**:
   ```bash
   aws configure list
   ```

3. **Test Individual Components**:
   ```bash
   # Test cost monitor
   E:/Projects/.venv/Scripts/python.exe E:/Projects/aws-cost-monitor.py --status
   
   # Test service monitor (single run)
   E:/Projects/.venv/Scripts/python.exe E:/Projects/monitorable-agent.py --single
   ```

4. **Check Log Files**:
   ```bash
   # View recent errors
   tail -n 50 E:/Projects/agent_logs/dev_focused_orchestrator.log
   ```

### **If Cost Monitor Fails**
- **AWS Credentials**: Run `aws configure` to set up credentials
- **Permissions**: Ensure Cost Explorer access in AWS IAM
- **Region**: Check AWS region settings

### **If Services Not Found**
- **Docker**: Make sure Docker services are running
  ```bash
  docker ps
  docker-compose up -d
  ```

## 📋 **WHAT EACH AGENT DOES**

| Agent | Purpose | Safe for Dev? |
|-------|---------|---------------|
| `aws-cost-monitor.py` | 🛡️ Monitors AWS costs, kills agents if spike | ✅ YES |
| `monitorable-agent.py` | 🔍 Tests service endpoints, health checks | ✅ YES |
| `log-monitor.py` | 📊 Real-time log viewing and status | ✅ YES |
| `gh-copilot-orchestrator.py` | 🤖 GitHub Copilot testing automation | ⚠️ MODERATE |
| `dev-focused-orchestrator.py` | 🎮 Manages all agents with auto-restart | ✅ YES |

## 🎯 **RECOMMENDED WORKFLOW**

1. **Start Simple**: Use `simple-dev-launcher.py` first
2. **Check Status**: Monitor with dashboard or logs
3. **Verify Costs**: Watch AWS cost monitoring
4. **Scale Up**: Add more agents if everything works
5. **Monitor**: Keep dashboard open for safety

## 🚨 **SAFETY FEATURES ACTIVE**

- ✅ **3% cost increase threshold** (dev environment)
- ✅ **30-minute monitoring window**
- ✅ **Global $25/hour failsafe**
- ✅ **Automatic agent restart**
- ✅ **Emergency shutdown capability**

## 💡 **TIPS**

- **Start with simple launcher first** to test everything works
- **Keep dashboard open** to monitor real-time status  
- **Check logs if agents fail** to understand issues
- **Use single-run mode** for testing: `--single` flag
- **Stop cleanly** with Ctrl+C instead of force killing
