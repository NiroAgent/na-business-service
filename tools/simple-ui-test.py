#!/usr/bin/env python3
"""
Simple UI Test - Verify dashboard content and JavaScript
"""

import requests
import json
import time
import re

def test_dashboard_content():
    """Test dashboard HTML content"""
    try:
        print("🧪 Testing Dashboard Content...")
        
        response = requests.get('http://localhost:5003', timeout=10)
        print(f"✅ Dashboard Response: {response.status_code}")
        
        content = response.text
        print(f"📊 Content Size: {len(content)} characters")
        
        # Check for essential elements
        checks = [
            ("🚀 AI Development Team Dashboard", "Title"),
            ("📊 Overview", "Overview Tab"),
            ("🤖 Agents", "Agents Tab"), 
            ("⚙️ System", "System Tab"),
            ("🔄 Pipeline", "Pipeline Tab"),
            ("function showTab", "JavaScript Function"),
            ("socket.io", "WebSocket"),
            ("dashboard_update", "Update Handler")
        ]
        
        results = []
        for check, name in checks:
            if check in content:
                print(f"✅ {name}: Found")
                results.append(True)
            else:
                print(f"❌ {name}: Missing")
                results.append(False)
        
        # Check for JavaScript syntax errors
        js_sections = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
        print(f"\n🔍 JavaScript Analysis:")
        for i, js in enumerate(js_sections):
            print(f"  Section {i+1}: {len(js)} characters")
            
            # Check for problematic patterns
            if 'return' in js and 'function' not in js.split('return')[0].split('\n')[-1]:
                print(f"  ⚠️  Potential illegal return statement")
            else:
                print(f"  ✅ No obvious syntax errors")
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📈 Content Validation: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate > 80
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def test_websocket_endpoint():
    """Test WebSocket endpoint availability"""
    try:
        print("\n🔌 Testing WebSocket Endpoint...")
        
        # Test socket.io endpoint
        response = requests.get('http://localhost:5003/socket.io/', timeout=5)
        print(f"✅ Socket.IO Response: {response.status_code}")
        
        return response.status_code in [200, 400]  # 400 is OK for GET on socket.io
        
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def test_agent_data():
    """Test if dashboard shows agent data"""
    try:
        print("\n🤖 Testing Agent Data...")
        
        response = requests.get('http://localhost:5003', timeout=10)
        content = response.text
        
        agent_indicators = [
            "AI Architect Agent",
            "AI Developer Agent", 
            "AI QA Agent",
            "Active Agents",
            "Phase 4"
        ]
        
        found = 0
        for indicator in agent_indicators:
            if indicator in content:
                print(f"✅ Found: {indicator}")
                found += 1
            else:
                print(f"❌ Missing: {indicator}")
        
        print(f"📊 Agent Data: {found}/{len(agent_indicators)} elements found")
        return found >= 3
        
    except Exception as e:
        print(f"❌ Agent data test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 SIMPLE UI TESTING SUITE")
    print("=" * 60)
    
    tests = [
        ("Dashboard Content", test_dashboard_content),
        ("WebSocket Endpoint", test_websocket_endpoint), 
        ("Agent Data", test_agent_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} PASSED ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Dashboard is working correctly.")
    else:
        print("⚠️  Some tests failed. Check dashboard functionality.")
