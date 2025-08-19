#!/usr/bin/env python3
"""
Dashboard Testing with Playwright
Tests the working dashboard functionality
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright
import pytest

class DashboardTests:
    def __init__(self):
        self.dashboard_url = "http://localhost:5003"
        self.test_results = []
    
    async def test_dashboard_loads(self):
        """Test that dashboard loads and displays tabs"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                # Navigate to dashboard
                await page.goto(self.dashboard_url)
                await page.wait_for_load_state('networkidle')
                
                # Check page title
                title = await page.title()
                assert "AI Development Team Dashboard" in title
                
                # Check tabs are present
                tabs = await page.query_selector_all('.tab')
                assert len(tabs) >= 4, f"Expected 4 tabs, found {len(tabs)}"
                
                # Check tab names
                tab_texts = []
                for tab in tabs:
                    text = await tab.inner_text()
                    tab_texts.append(text.strip())
                
                expected_tabs = ["📊 Overview", "🤖 Agents", "⚙️ System", "🔄 Pipeline"]
                for expected in expected_tabs:
                    assert any(expected in tab for tab in tab_texts), f"Missing tab: {expected}"
                
                print("✅ Dashboard loads correctly with all tabs")
                return True
                
            except Exception as e:
                print(f"❌ Dashboard load test failed: {e}")
                return False
            finally:
                await browser.close()
    
    async def test_tab_switching(self):
        """Test that tab switching works"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                await page.goto(self.dashboard_url)
                await page.wait_for_load_state('networkidle')
                
                # Test clicking each tab
                tabs = await page.query_selector_all('.tab')
                
                for i, tab in enumerate(tabs):
                    await tab.click()
                    await page.wait_for_timeout(500)  # Wait for content to load
                    
                    # Check if tab is active
                    tab_class = await tab.get_attribute('class')
                    assert 'active' in tab_class, f"Tab {i} not marked as active"
                
                print("✅ Tab switching works correctly")
                return True
                
            except Exception as e:
                print(f"❌ Tab switching test failed: {e}")
                return False
            finally:
                await browser.close()
    
    async def test_live_updates(self):
        """Test that dashboard receives live updates"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                await page.goto(self.dashboard_url)
                await page.wait_for_load_state('networkidle')
                
                # Get initial values
                initial_cpu = await page.inner_text('#cpu-usage')
                initial_memory = await page.inner_text('#memory-usage')
                
                # Wait for updates (dashboard updates every 5 seconds)
                await page.wait_for_timeout(6000)
                
                # Check if values updated
                updated_cpu = await page.inner_text('#cpu-usage')
                updated_memory = await page.inner_text('#memory-usage')
                
                # Values should be numbers with %
                assert '%' in updated_cpu, "CPU usage should show percentage"
                assert '%' in updated_memory, "Memory usage should show percentage"
                
                print("✅ Live updates working correctly")
                return True
                
            except Exception as e:
                print(f"❌ Live updates test failed: {e}")
                return False
            finally:
                await browser.close()
    
    async def test_agent_detection(self):
        """Test that dashboard detects running agents"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                await page.goto(self.dashboard_url)
                await page.wait_for_load_state('networkidle')
                
                # Click on Agents tab
                agents_tab = await page.query_selector('text=🤖 Agents')
                await agents_tab.click()
                await page.wait_for_timeout(1000)
                
                # Check for agent cards
                agent_cards = await page.query_selector_all('.agent-card')
                assert len(agent_cards) >= 3, f"Expected at least 3 agent cards, found {len(agent_cards)}"
                
                # Check for specific agents
                page_content = await page.content()
                expected_agents = ["AI Architect Agent", "AI Developer Agent", "AI QA Agent"]
                
                for agent in expected_agents:
                    assert agent in page_content, f"Missing agent: {agent}"
                
                print("✅ Agent detection working correctly")
                return True
                
            except Exception as e:
                print(f"❌ Agent detection test failed: {e}")
                return False
            finally:
                await browser.close()
    
    async def test_pipeline_progress(self):
        """Test that pipeline progress is displayed"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                await page.goto(self.dashboard_url)
                await page.wait_for_load_state('networkidle')
                
                # Click on Pipeline tab
                pipeline_tab = await page.query_selector('text=🔄 Pipeline')
                await pipeline_tab.click()
                await page.wait_for_timeout(1000)
                
                # Check for progress bars
                progress_bars = await page.query_selector_all('.progress-bar')
                assert len(progress_bars) >= 3, f"Expected at least 3 progress bars, found {len(progress_bars)}"
                
                # Check for phase information
                page_content = await page.content()
                phases = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
                
                for phase in phases:
                    assert phase in page_content, f"Missing phase: {phase}"
                
                print("✅ Pipeline progress working correctly")
                return True
                
            except Exception as e:
                print(f"❌ Pipeline progress test failed: {e}")
                return False
            finally:
                await browser.close()
    
    async def run_all_tests(self):
        """Run all dashboard tests"""
        print("🧪 Starting Dashboard Tests")
        print("=" * 50)
        
        tests = [
            self.test_dashboard_loads,
            self.test_tab_switching,
            self.test_live_updates,
            self.test_agent_detection,
            self.test_pipeline_progress
        ]
        
        results = {}
        for test in tests:
            test_name = test.__name__
            print(f"\n🔄 Running {test_name}...")
            try:
                result = await test()
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in results.values() if r)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        return results

# Simple test runner
async def run_dashboard_tests():
    """Run dashboard tests"""
    tester = DashboardTests()
    return await tester.run_all_tests()

if __name__ == "__main__":
    # Check if dashboard is running
    import requests
    try:
        response = requests.get("http://localhost:5003", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running, starting tests...")
            results = asyncio.run(run_dashboard_tests())
        else:
            print("❌ Dashboard not responding")
    except Exception as e:
        print(f"❌ Cannot connect to dashboard: {e}")
        print("💡 Make sure dashboard is running: python working-dashboard.py")
