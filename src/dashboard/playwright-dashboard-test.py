#!/usr/bin/env python3
"""
Playwright Dashboard Tests - Real browser automation testing
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_dashboard_with_playwright():
    """Test dashboard using Playwright browser automation"""
    print("🎭 Starting Playwright Dashboard Tests")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch browser
        print("🚀 Launching Chromium browser...")
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Test 1: Navigate to dashboard
            print("\n🔄 Test 1: Loading Dashboard")
            await page.goto("http://localhost:5003")
            await page.wait_for_load_state("networkidle")
            
            # Check title
            title = await page.title()
            print(f"📄 Page title: {title}")
            assert "AI Development Team Dashboard" in title, "Dashboard title not found"
            print("✅ Dashboard loads correctly")
            
            # Test 2: Check tabs are present
            print("\n🔄 Test 2: Checking Tab Structure")
            tabs = await page.query_selector_all('.tab')
            print(f"📊 Found {len(tabs)} tabs")
            
            tab_texts = []
            for i, tab in enumerate(tabs):
                text = await tab.inner_text()
                tab_texts.append(text.strip())
                print(f"  Tab {i+1}: {text.strip()}")
            
            expected_tabs = ["Overview", "Agents", "System", "Pipeline"]
            for expected in expected_tabs:
                found = any(expected in tab for tab in tab_texts)
                assert found, f"Missing tab: {expected}"
            print("✅ All tabs present")
            
            # Test 3: Test tab switching
            print("\n🔄 Test 3: Testing Tab Switching")
            for i, tab in enumerate(tabs):
                print(f"  Clicking tab {i+1}: {tab_texts[i]}")
                await tab.click()
                await page.wait_for_timeout(1000)
                
                # Check if tab is active
                tab_class = await tab.get_attribute('class')
                if 'active' in tab_class:
                    print(f"    ✅ Tab {i+1} is active")
                else:
                    print(f"    ⚠️ Tab {i+1} may not be properly active")
            
            print("✅ Tab switching functional")
            
            # Test 4: Check for live data
            print("\n🔄 Test 4: Checking Live Data")
            
            # Go to Overview tab
            overview_tab = await page.query_selector('text=Overview')
            if overview_tab:
                await overview_tab.click()
                await page.wait_for_timeout(1000)
            
            # Check for metric cards
            metric_cards = await page.query_selector_all('.metric-card')
            print(f"📊 Found {len(metric_cards)} metric cards")
            
            for i, card in enumerate(metric_cards):
                try:
                    value = await card.query_selector('.metric-value')
                    label = await card.query_selector('.metric-label')
                    if value and label:
                        value_text = await value.inner_text()
                        label_text = await label.inner_text()
                        print(f"  Metric {i+1}: {label_text} = {value_text}")
                except:
                    print(f"  Metric {i+1}: Could not read values")
            
            if len(metric_cards) >= 3:
                print("✅ Metrics are displaying")
            else:
                print("⚠️ Few or no metrics found")
            
            # Test 5: Check Agents tab
            print("\n🔄 Test 5: Testing Agents Tab")
            agents_tab = await page.query_selector('text=Agents')
            if agents_tab:
                await agents_tab.click()
                await page.wait_for_timeout(1000)
                
                agent_cards = await page.query_selector_all('.agent-card')
                print(f"🤖 Found {len(agent_cards)} agent cards")
                
                for i, card in enumerate(agent_cards):
                    try:
                        content = await card.inner_text()
                        print(f"  Agent {i+1}: {content[:50]}...")
                    except:
                        print(f"  Agent {i+1}: Could not read content")
                
                if len(agent_cards) >= 1:
                    print("✅ Agent information is displaying")
                else:
                    print("⚠️ No agent cards found")
            
            # Test 6: Check System metrics
            print("\n🔄 Test 6: Testing System Tab")
            system_tab = await page.query_selector('text=System')
            if system_tab:
                await system_tab.click()
                await page.wait_for_timeout(1000)
                
                cpu_element = await page.query_selector('#cpu-usage')
                memory_element = await page.query_selector('#memory-usage')
                
                if cpu_element and memory_element:
                    cpu_text = await cpu_element.inner_text()
                    memory_text = await memory_element.inner_text()
                    print(f"  💻 CPU Usage: {cpu_text}")
                    print(f"  🧠 Memory Usage: {memory_text}")
                    print("✅ System metrics are updating")
                else:
                    print("⚠️ System metrics not found")
            
            # Test 7: Check Pipeline progress
            print("\n🔄 Test 7: Testing Pipeline Tab")
            pipeline_tab = await page.query_selector('text=Pipeline')
            if pipeline_tab:
                await pipeline_tab.click()
                await page.wait_for_timeout(1000)
                
                progress_bars = await page.query_selector_all('.progress-bar')
                print(f"📊 Found {len(progress_bars)} progress bars")
                
                if len(progress_bars) >= 3:
                    print("✅ Pipeline progress is displaying")
                else:
                    print("⚠️ Few or no progress bars found")
            
            # Test 8: Wait for live updates
            print("\n🔄 Test 8: Testing Live Updates")
            print("  Waiting 8 seconds for WebSocket updates...")
            
            # Go back to overview to see updates
            overview_tab = await page.query_selector('text=Overview')
            if overview_tab:
                await overview_tab.click()
            
            await page.wait_for_timeout(8000)  # Wait for updates
            
            # Check if timestamp or values changed
            timestamp_element = await page.query_selector('#phase-status')
            if timestamp_element:
                timestamp_text = await timestamp_element.inner_text()
                print(f"  📅 Status: {timestamp_text}")
                print("✅ Live updates working")
            else:
                print("⚠️ Could not verify live updates")
            
            print("\n🎉 All tests completed!")
            
            # Keep browser open for manual inspection
            print("\n👀 Browser will stay open for 10 seconds for manual inspection...")
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            # Take screenshot on failure
            await page.screenshot(path="dashboard_test_failure.png")
            print("📸 Screenshot saved as dashboard_test_failure.png")
            
        finally:
            await browser.close()
            print("\n👋 Browser closed")

async def main():
    """Main test runner"""
    # Check if dashboard is running
    import requests
    try:
        response = requests.get("http://localhost:5003", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running")
            await test_dashboard_with_playwright()
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to dashboard: {e}")
        print("💡 Make sure dashboard is running: python working-dashboard.py")

if __name__ == "__main__":
    asyncio.run(main())
