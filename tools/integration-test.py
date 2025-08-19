#!/usr/bin/env python3
"""
Integration Test Script for AI Development Team Infrastructure
Tests communication between all components
"""

import time
import json
import requests
import threading
from datetime import datetime

def test_dashboard_api():
    """Test enhanced dashboard API"""
    try:
        response = requests.get('http://localhost:5003/api/data', timeout=5)
        if response.status_code == 200:
            data = response.json()
            required_keys = ['agents', 'team_metrics', 'github_integration']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                print(f"❌ Dashboard API missing keys: {missing_keys}")
                return False
            else:
                print("✅ Dashboard API enhanced successfully")
                print(f"   - Team metrics: {data['team_metrics']}")
                print(f"   - GitHub integration: {data['github_integration']}")
                return True
        else:
            print(f"❌ Dashboard API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard API connection failed: {e}")
        return False

def test_team_communication():
    """Test team communication protocol"""
    try:
        # Try to import and test team communication
        import sys
        sys.path.append('/e/Projects')
        
        from team_communication_protocol import TeamCommunicationHub, AgentRole, MessageType, create_work_assignment
        
        hub = TeamCommunicationHub()
        
        # Register test agents
        hub.register_agent("test_pm", AgentRole.PRODUCT_MANAGER, ["planning", "coordination"])
        hub.register_agent("test_dev", AgentRole.BACKEND_DEVELOPER, ["python", "api", "database"])
        
        # Send test message
        work_msg = create_work_assignment("test_pm", "test_dev", "TEST-001", "Test work assignment")
        success = hub.send_message(work_msg)
        
        # Check message delivery
        messages = hub.get_messages("test_dev")
        
        if success and len(messages) > 0:
            print("✅ Team communication protocol working")
            print(f"   - Agents registered: {len(hub.agent_registry)}")
            print(f"   - Messages delivered: {len(messages)}")
            return True
        else:
            print("❌ Team communication protocol failed")
            return False
            
    except Exception as e:
        print(f"❌ Team communication test failed: {e}")
        return False

def test_work_queue():
    """Test work queue management"""
    try:
        from work_queue_manager import WorkQueueManager, create_github_issue_work_item
        
        wqm = WorkQueueManager()
        
        # Register test agent
        wqm.register_agent("test_backend", ["python", "api"], 5)
        
        # Create test work item
        work_item = create_github_issue_work_item(
            "TEST-001", 
            "Test Issue", 
            "Test description", 
            ["backend", "high"], 
            "test-repo"
        )
        
        # Add to queue
        success = wqm.add_work_item(work_item)
        
        # Start auto-assignment briefly
        wqm.start_auto_assignment()
        time.sleep(2)
        wqm.stop_auto_assignment()
        
        # Check queue status
        status = wqm.get_queue_status()
        
        if success and status['total_items'] > 0:
            print("✅ Work queue management working")
            print(f"   - Total items: {status['total_items']}")
            print(f"   - Registered agents: {len(status['agents'])}")
            return True
        else:
            print("❌ Work queue management failed")
            return False
            
    except Exception as e:
        print(f"❌ Work queue test failed: {e}")
        return False

def test_existing_systems():
    """Test existing intelligence systems"""
    results = {}
    
    # Check if intelligence systems are running
    try:
        response = requests.get('http://localhost:5003', timeout=5)
        results['dashboard'] = response.status_code == 200
    except:
        results['dashboard'] = False
    
    # Check for intelligence system files
    import os
    results['issue_detector'] = os.path.exists('/e/Projects/intelligent-issue-detector.py')
    results['self_healing'] = os.path.exists('/e/Projects/agent-self-healing.py')
    results['communication_hub'] = os.path.exists('/e/Projects/agent-communication-hub.py')
    
    print("🔍 Existing Systems Status:")
    for system, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {system.replace('_', ' ').title()}")
    
    return all(results.values())

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running AI Development Team Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Dashboard API", test_dashboard_api),
        ("Team Communication", test_team_communication),
        ("Work Queue", test_work_queue),
        ("Existing Systems", test_existing_systems)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔬 Testing {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 Integration Test Results:")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status_icon = "✅" if result else "❌"
        print(f"   {status_icon} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems ready for Claude Opus integration!")
        return True
    else:
        print("⚠️  Some systems need attention before Claude Opus can proceed")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
