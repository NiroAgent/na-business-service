#!/usr/bin/env python3
"""
Complete System Status Check - Verify all components are working
"""

import requests
import json
import os
import time
from datetime import datetime
import subprocess
import psutil

def check_dashboard_status():
    """Check if dashboard is responding"""
    print("🔍 DASHBOARD STATUS CHECK")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:5003", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # Check for key elements
            elements = {
                "Title": "AI Development Team Dashboard" in content,
                "Overview Tab": "Overview" in content,
                "Agents Tab": "Agents" in content,
                "System Tab": "System" in content,
                "Pipeline Tab": "Pipeline" in content,
                "WebSocket": "socket.io" in content,
                "CSS Styling": "tab-content" in content
            }
            
            print(f"📊 Dashboard Response: {response.status_code}")
            print(f"📄 Content Length: {len(content)} bytes")
            
            for element, found in elements.items():
                status = "✅" if found else "❌"
                print(f"{status} {element}")
            
            all_good = all(elements.values())
            if all_good:
                print("🎉 Dashboard is fully functional!")
            else:
                print("⚠️ Dashboard has some missing elements")
            
            return all_good
            
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard check failed: {e}")
        return False

def check_agent_processes():
    """Check for running agent processes"""
    print("\n🤖 AGENT PROCESSES CHECK")
    print("-" * 30)
    
    agent_keywords = ['ai-developer', 'ai-architect', 'ai-qa', 'github-issues', 'agent-activity-simulator']
    found_agents = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                for keyword in agent_keywords:
                    if keyword in cmdline:
                        found_agents.append({
                            'pid': proc.info['pid'],
                            'name': keyword,
                            'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                        })
                        break
        except:
            continue
    
    print(f"🔍 Found {len(found_agents)} agent processes:")
    for agent in found_agents:
        print(f"  ✅ {agent['name']} (PID: {agent['pid']})")
        print(f"     {agent['cmdline']}")
    
    if len(found_agents) == 0:
        print("⚠️ No agent processes detected")
    
    return found_agents

def check_project_files():
    """Check for generated project files"""
    print("\n📁 PROJECT FILES CHECK")
    print("-" * 30)
    
    checks = [
        ("Test Projects", "test-projects"),
        ("Agent Activity Log", "agent_activity.log"),
        ("Agent Simulation State", "agent_simulation_state.json"),
        ("Policy Database", "agent_policies.db")
    ]
    
    files_found = 0
    for name, path in checks:
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
            if os.path.isfile(path):
                size = os.path.getsize(path)
                print(f"   Size: {size} bytes")
            files_found += 1
        else:
            print(f"❌ {name}: {path} (not found)")
    
    # Check test project directories
    if os.path.exists("test-projects"):
        projects = [d for d in os.listdir("test-projects") if os.path.isdir(os.path.join("test-projects", d))]
        print(f"📊 Test Projects: {len(projects)} found")
        for project in projects:
            print(f"   📁 {project}")
    
    return files_found

def check_generated_files():
    """Check for recently generated files"""
    print("\n📄 GENERATED FILES CHECK")
    print("-" * 30)
    
    if os.path.exists("test-projects/ecommerce-api/generated"):
        generated_dir = "test-projects/ecommerce-api/generated"
        files = os.listdir(generated_dir)
        print(f"📊 Generated Files: {len(files)} found")
        
        for file in files[:10]:  # Show first 10
            file_path = os.path.join(generated_dir, file)
            if os.path.isfile(file_path):
                mtime = os.path.getmtime(file_path)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"   📄 {file} (modified: {mtime_str})")
        
        if len(files) > 10:
            print(f"   ... and {len(files) - 10} more files")
        
        return len(files)
    else:
        print("❌ No generated files directory found")
        return 0

def test_dashboard_interactivity():
    """Test dashboard API endpoints"""
    print("\n🔗 DASHBOARD API CHECK")
    print("-" * 30)
    
    endpoints = [
        ("/", "Main page"),
        ("/api/data", "Data API")
    ]
    
    working_endpoints = 0
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:5003{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"✅ {description}: {endpoint}")
                working_endpoints += 1
            else:
                print(f"⚠️ {description}: {endpoint} (status: {response.status_code})")
        except Exception as e:
            print(f"❌ {description}: {endpoint} (error: {e})")
    
    return working_endpoints

def run_complete_status_check():
    """Run complete system status check"""
    print("🔍 COMPLETE SYSTEM STATUS CHECK")
    print("=" * 50)
    print(f"📅 Time: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Run all checks
    dashboard_ok = check_dashboard_status()
    agents = check_agent_processes()
    files_count = check_project_files()
    generated_count = check_generated_files()
    api_count = test_dashboard_interactivity()
    
    # Summary
    print("\n📊 OVERALL SYSTEM STATUS")
    print("=" * 50)
    
    status_items = [
        ("Dashboard", "✅ Working" if dashboard_ok else "❌ Issues"),
        ("Agents Running", f"✅ {len(agents)} active" if len(agents) > 0 else "⚠️ None detected"),
        ("Project Files", f"✅ {files_count} found" if files_count > 0 else "⚠️ Missing"),
        ("Generated Files", f"✅ {generated_count} created" if generated_count > 0 else "⚠️ None"),
        ("API Endpoints", f"✅ {api_count} working" if api_count > 0 else "❌ Not responding")
    ]
    
    for item, status in status_items:
        print(f"{status:<20} {item}")
    
    # Overall health score
    scores = [dashboard_ok, len(agents) > 0, files_count > 0, generated_count > 0, api_count > 0]
    health_score = sum(scores) / len(scores) * 100
    
    print(f"\n🎯 Overall System Health: {health_score:.1f}%")
    
    if health_score >= 80:
        print("🎉 System is working well!")
        print("💡 Ready for Opus to continue with AI QA Agent")
    elif health_score >= 60:
        print("⚠️ System is partially working")
        print("💡 Some components need attention")
    else:
        print("❌ System needs significant fixes")
        print("💡 Multiple components not working")
    
    # Save status to file
    status_data = {
        "timestamp": datetime.now().isoformat(),
        "dashboard_ok": dashboard_ok,
        "agents_count": len(agents),
        "agents": agents,
        "files_count": files_count,
        "generated_count": generated_count,
        "api_count": api_count,
        "health_score": health_score
    }
    
    with open("system_status_report.json", 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"\n📄 Status report saved to: system_status_report.json")
    
    return status_data

if __name__ == "__main__":
    status = run_complete_status_check()
