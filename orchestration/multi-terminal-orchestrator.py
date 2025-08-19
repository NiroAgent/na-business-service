#!/usr/bin/env python3
"""
Multi-Terminal Agent Orchestrator
Launches agents in separate terminal windows for visibility
Or runs them hidden in background based on preference
"""

import subprocess
import os
import time
import json
from pathlib import Path
from datetime import datetime
import threading
import psutil

class MultiTerminalOrchestrator:
    def __init__(self, show_terminals=True):
        self.show_terminals = show_terminals
        self.base_dir = Path("E:/Projects")
        self.processes = {}
        self.terminals = []
        
        # Terminal configurations
        self.terminal_configs = {
            'sdlc-iterator': {
                'title': 'SDLC Iterator Agent',
                'script': 'sdlc-iterator-agent.py',
                'args': '--continuous',
                'color': '0A',  # Green on black
                'position': '0,0',
                'size': '120,30'
            },
            'issue-monitor': {
                'title': 'Issue Monitor Agent',
                'script': 'issue-driven-local-agent.py',
                'args': '--monitor',
                'color': '0B',  # Cyan on black
                'position': '650,0',
                'size': '120,30'
            },
            'ns-auth': {
                'title': 'NiroSubs Auth Agent',
                'script': 'local-agent-system.py',
                'args': '--service ns-auth',
                'color': '0E',  # Yellow on black
                'position': '0,400',
                'size': '60,25'
            },
            'ns-dashboard': {
                'title': 'NiroSubs Dashboard Agent',
                'script': 'local-agent-system.py',
                'args': '--service ns-dashboard',
                'color': '0D',  # Purple on black
                'position': '650,400',
                'size': '60,25'
            },
            'vf-audio': {
                'title': 'VisualForge Audio Agent',
                'script': 'local-agent-system.py',
                'args': '--service vf-audio-service',
                'color': '0C',  # Red on black
                'position': '1300,0',
                'size': '60,25'
            },
            'vf-video': {
                'title': 'VisualForge Video Agent',
                'script': 'local-agent-system.py',
                'args': '--service vf-video-service',
                'color': '09',  # Blue on black
                'position': '1300,400',
                'size': '60,25'
            }
        }
    
    def launch_terminal_window(self, name: str, config: dict):
        """Launch agent in a new terminal window"""
        
        script_path = self.base_dir / config['script']
        title = config['title']
        
        if self.show_terminals:
            # Launch in visible terminal window
            if os.name == 'nt':  # Windows
                # Use Windows Terminal if available, otherwise cmd
                if self.check_windows_terminal():
                    cmd = self.build_windows_terminal_command(name, config)
                else:
                    cmd = self.build_cmd_command(name, config)
            else:  # Linux/Mac
                cmd = self.build_unix_terminal_command(name, config)
            
            print(f"🖥️  Launching {title} in new terminal...")
            process = subprocess.Popen(cmd, shell=True)
            
        else:
            # Launch hidden in background
            print(f"👻 Launching {title} in background...")
            cmd = f"python {script_path} {config['args']}"
            
            if os.name == 'nt':
                # Windows - hide window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo,
                    cwd=str(self.base_dir)
                )
            else:
                # Unix - run in background
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(self.base_dir)
                )
        
        self.processes[name] = process
        return process
    
    def check_windows_terminal(self) -> bool:
        """Check if Windows Terminal is available"""
        try:
            result = subprocess.run("wt --version", shell=True, capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def build_windows_terminal_command(self, name: str, config: dict) -> str:
        """Build Windows Terminal command"""
        script_path = self.base_dir / config['script']
        
        # Windows Terminal with tabs
        cmd = f'wt -w 0 new-tab --title "{config["title"]}" --suppressApplicationTitle '
        cmd += f'--colorScheme "Campbell" '
        cmd += f'cmd /k "cd /d {self.base_dir} && python {script_path} {config["args"]}"'
        
        return cmd
    
    def build_cmd_command(self, name: str, config: dict) -> str:
        """Build cmd.exe command"""
        script_path = self.base_dir / config['script']
        position = config['position'].split(',')
        
        # Create batch file for each agent
        batch_content = f"""@echo off
title {config['title']}
color {config['color']}
cd /d {self.base_dir}
echo ========================================
echo     {config['title']}
echo ========================================
echo.
python {script_path} {config['args']}
pause
"""
        
        batch_file = self.base_dir / f"agent_{name}.bat"
        batch_file.write_text(batch_content)
        
        # Launch with position
        cmd = f'start "{config["title"]}" cmd /c "{batch_file}"'
        
        return cmd
    
    def build_unix_terminal_command(self, name: str, config: dict) -> str:
        """Build Unix terminal command"""
        script_path = self.base_dir / config['script']
        
        # Try different terminal emulators
        terminals = [
            f'gnome-terminal --title="{config["title"]}" -- python3 {script_path} {config["args"]}',
            f'xterm -title "{config["title"]}" -e python3 {script_path} {config["args"]}',
            f'konsole --title "{config["title"]}" -e python3 {script_path} {config["args"]}'
        ]
        
        # Return first available
        return terminals[0]
    
    def launch_all_agents(self, selection: list = None):
        """Launch all selected agents"""
        
        if selection is None:
            selection = list(self.terminal_configs.keys())
        
        print("\n" + "="*60)
        print("🚀 MULTI-TERMINAL AGENT ORCHESTRATOR")
        print(f"Mode: {'Visible Terminals' if self.show_terminals else 'Background'}")
        print(f"Agents to launch: {len(selection)}")
        print("="*60 + "\n")
        
        for name in selection:
            if name in self.terminal_configs:
                config = self.terminal_configs[name]
                self.launch_terminal_window(name, config)
                time.sleep(2)  # Delay between launches
        
        print(f"\n✅ Launched {len(selection)} agents")
        
        if self.show_terminals:
            print("\n📺 Terminal Windows:")
            for name in selection:
                print(f"   - {self.terminal_configs[name]['title']}")
            print("\nEach agent is running in its own terminal window.")
            print("You can switch between them to monitor progress.")
        else:
            print("\n👻 Agents running in background")
            print("Use the monitor dashboard to check status")
    
    def create_monitor_dashboard(self):
        """Create a monitoring dashboard in a terminal"""
        
        dashboard_script = f"""
import time
import psutil
import subprocess
from datetime import datetime

def get_agent_status():
    agents = {list(self.terminal_configs.keys())}
    status = {{}}
    
    for agent in agents:
        # Check if process is running
        running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if agent in cmdline or agent.replace('-', '_') in cmdline:
                    running = True
                    break
            except:
                pass
        status[agent] = running
    
    return status

def display_dashboard():
    while True:
        # Clear screen
        print('\\033[2J\\033[H')  # ANSI escape codes
        
        print("="*60)
        print("    AGENT MONITORING DASHBOARD")
        print("="*60)
        print(f"Time: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
        print()
        
        # System resources
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        print(f"System: CPU {{cpu:.1f}}% | Memory {{memory:.1f}}%")
        print()
        
        # Agent status
        print("Agent Status:")
        print("-" * 40)
        
        status = get_agent_status()
        for agent, running in status.items():
            icon = "🟢" if running else "🔴"
            print(f"{{icon}} {{agent:20}} {{'Running' if running else 'Stopped':10}}")
        
        print()
        print("Press Ctrl+C to exit dashboard")
        print("="*60)
        
        time.sleep(5)  # Refresh every 5 seconds

if __name__ == "__main__":
    try:
        display_dashboard()
    except KeyboardInterrupt:
        print("\\nDashboard closed")
"""
        
        # Save dashboard script
        dashboard_file = self.base_dir / "agent_dashboard.py"
        dashboard_file.write_text(dashboard_script)
        
        if self.show_terminals:
            # Launch dashboard in its own terminal
            if os.name == 'nt':
                cmd = f'start "Agent Dashboard" cmd /k "cd /d {self.base_dir} && python agent_dashboard.py"'
            else:
                cmd = f'gnome-terminal --title="Agent Dashboard" -- python3 {dashboard_file}'
            
            subprocess.Popen(cmd, shell=True)
            print("📊 Dashboard launched in separate terminal")
        
        return dashboard_file
    
    def stop_all_agents(self):
        """Stop all running agents"""
        
        print("\n⏹️  Stopping all agents...")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"   Stopping {name}...")
                process.terminate()
                time.sleep(1)
                if process.poll() is None:
                    process.kill()
        
        # Clean up batch files
        for batch_file in self.base_dir.glob("agent_*.bat"):
            batch_file.unlink(missing_ok=True)
        
        print("✅ All agents stopped")

def create_launcher_script():
    """Create launcher script with terminal options"""
    
    launcher = """@echo off
REM Multi-Terminal Agent Launcher

echo ========================================
echo   MULTI-TERMINAL AGENT ORCHESTRATOR
echo ========================================
echo.
echo Display Options:
echo.
echo 1. VISIBLE TERMINALS - See each agent in its own window
echo 2. BACKGROUND MODE - Run hidden (use dashboard to monitor)
echo 3. MIXED MODE - Some visible, some hidden
echo 4. DASHBOARD ONLY - Just monitoring dashboard
echo.
set /p mode="Select mode (1-4): "

echo.
echo Agent Selection:
echo.
echo A. ALL AGENTS - Launch everything
echo S. SDLC ONLY - Just SDLC iterator
echo I. ISSUES ONLY - Just issue monitor
echo N. NIROSUBS - NiroSubs services only
echo V. VISUALFORGE - VisualForge services only
echo C. CUSTOM - Choose specific agents
echo.
set /p selection="Select agents (A/S/I/N/V/C): "

if "%mode%"=="1" (
    set visibility=--visible
) else if "%mode%"=="2" (
    set visibility=--hidden
) else if "%mode%"=="3" (
    set visibility=--mixed
) else (
    set visibility=--dashboard-only
)

if "%selection%"=="A" (
    set agents=all
) else if "%selection%"=="S" (
    set agents=sdlc-iterator
) else if "%selection%"=="I" (
    set agents=issue-monitor
) else if "%selection%"=="N" (
    set agents=ns-auth,ns-dashboard
) else if "%selection%"=="V" (
    set agents=vf-audio,vf-video
) else (
    echo Enter agent names separated by commas:
    set /p agents="Agents: "
)

echo.
echo Launching with options:
echo   Display: %visibility%
echo   Agents: %agents%
echo.

python E:\\Projects\\multi-terminal-orchestrator.py %visibility% --agents %agents%

pause
"""
    
    launcher_file = Path("E:/Projects/launch-multi-terminal.bat")
    launcher_file.write_text(launcher)
    
    print(f"✅ Created launcher: {launcher_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Terminal Agent Orchestrator')
    parser.add_argument('--visible', action='store_true', help='Show terminal windows')
    parser.add_argument('--hidden', action='store_true', help='Run in background')
    parser.add_argument('--mixed', action='store_true', help='Some visible, some hidden')
    parser.add_argument('--dashboard-only', action='store_true', help='Just launch dashboard')
    parser.add_argument('--agents', help='Comma-separated agent names or "all"')
    parser.add_argument('--stop', action='store_true', help='Stop all agents')
    parser.add_argument('--create-launcher', action='store_true', help='Create launcher script')
    
    args = parser.parse_args()
    
    if args.create_launcher:
        create_launcher_script()
        return
    
    # Determine visibility mode
    show_terminals = True
    if args.hidden:
        show_terminals = False
    elif args.mixed:
        show_terminals = 'mixed'
    
    orchestrator = MultiTerminalOrchestrator(show_terminals)
    
    if args.stop:
        orchestrator.stop_all_agents()
        return
    
    if args.dashboard_only:
        orchestrator.create_monitor_dashboard()
        print("Dashboard launched. Press Ctrl+C in dashboard window to exit.")
        return
    
    # Parse agent selection
    if args.agents:
        if args.agents == 'all':
            selection = None
        else:
            selection = [a.strip() for a in args.agents.split(',')]
    else:
        selection = None
    
    # Launch agents
    orchestrator.launch_all_agents(selection)
    
    # Create monitoring dashboard
    orchestrator.create_monitor_dashboard()
    
    # Keep running
    try:
        print("\n💡 Tips:")
        print("- Each agent runs in its own terminal window")
        print("- Check the dashboard terminal for overall status")
        print("- Press Ctrl+C here to stop all agents")
        print("\nPress Ctrl+C to stop all agents...")
        
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nStopping agents...")
        orchestrator.stop_all_agents()

if __name__ == "__main__":
    main()