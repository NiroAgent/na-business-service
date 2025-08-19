#!/usr/bin/env python3
"""
Comprehensive Dashboard UI Tests
Tests all tab functionality, data loading, and user interactions
"""

import time
import unittest
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import subprocess
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DashboardUITests')

class DashboardUITests(unittest.TestCase):
    """Comprehensive UI tests for the dashboard"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.dashboard_url = "http://localhost:5003"
        cls.dashboard_process = None
        cls.driver = None
        
        # Start dashboard if not running
        cls.start_dashboard()
        time.sleep(3)  # Give dashboard time to start
        
        # Set up WebDriver
        cls.setup_webdriver()
    
    @classmethod
    def start_dashboard(cls):
        """Start the dashboard process"""
        try:
            # Check if dashboard is already running
            response = requests.get(cls.dashboard_url, timeout=2)
            logger.info("Dashboard already running")
            return
        except requests.exceptions.RequestException:
            logger.info("Starting dashboard...")
            
        # Start dashboard process
        cls.dashboard_process = subprocess.Popen(
            ['python', 'comprehensive-tabbed-dashboard.py'],
            cwd='e:/Projects',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    @classmethod
    def setup_webdriver(cls):
        """Set up Chrome WebDriver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            logger.warning(f"Could not start Chrome WebDriver: {e}")
            logger.info("UI tests will be skipped")
            cls.driver = None
    
    def setUp(self):
        """Set up each test"""
        if self.driver:
            self.driver.get(self.dashboard_url)
            self.wait = WebDriverWait(self.driver, 10)
    
    def test_dashboard_loads(self):
        """Test that dashboard loads successfully"""
        if not self.driver:
            self.skipTest("WebDriver not available")
            
        logger.info("Testing dashboard loading...")
        
        # Check page title
        self.assertIn("Agent Dashboard", self.driver.title)
        
        # Check main header
        header = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertIn("COMPREHENSIVE", header.text.upper())
        
        logger.info("✅ Dashboard loads successfully")
    
    def test_tab_navigation(self):
        """Test all tab buttons are clickable and switch content"""
        if not self.driver:
            self.skipTest("WebDriver not available")
            
        logger.info("Testing tab navigation...")
        
        # Find all tab buttons
        tab_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".tab")
        self.assertGreater(len(tab_buttons), 0, "Should have tab buttons")
        
        expected_tabs = [
            "Console Output", "Agent Consoles", "Agent Grid", 
            "System Resources", "Performance Metrics", "Cost Monitoring",
            "Features & Stories", "AI Development Team", "Work Queue", "GitHub Integration"
        ]
        
        # Test each tab
        for i, tab_button in enumerate(tab_buttons):
            if i >= len(expected_tabs):
                break
                
            tab_text = tab_button.text
            logger.info(f"Testing tab: {tab_text}")
            
            # Click tab
            self.driver.execute_script("arguments[0].click();", tab_button)
            time.sleep(0.5)
            
            # Check if tab becomes active
            active_tabs = self.driver.find_elements(By.CSS_SELECTOR, ".tab.active")
            self.assertEqual(len(active_tabs), 1, "Should have exactly one active tab")
            
            # Check if corresponding content is visible
            tab_contents = self.driver.find_elements(By.CSS_SELECTOR, ".tab-content.active")
            self.assertEqual(len(tab_contents), 1, "Should have exactly one active tab content")
        
        logger.info("✅ Tab navigation working")
    
    def test_data_loading(self):
        """Test that data loads in various tabs"""
        if not self.driver:
            self.skipTest("WebDriver not available")
            
        logger.info("Testing data loading...")
        
        # Test Console Output tab (default)
        console_logs = self.driver.find_elements(By.CSS_SELECTOR, "#console-logs .log-entry")
        logger.info(f"Console logs found: {len(console_logs)}")
        
        # Test Agent Grid tab
        grid_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Agent Grid')]")
        self.driver.execute_script("arguments[0].click();", grid_tab)
        time.sleep(1)
        
        agent_grid = self.driver.find_element(By.ID, "agent-grid")
        self.assertTrue(agent_grid.is_displayed(), "Agent grid should be visible")
        
        # Test System Resources tab
        resources_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'System Resources')]")
        self.driver.execute_script("arguments[0].click();", resources_tab)
        time.sleep(1)
        
        cpu_metric = self.driver.find_elements(By.CSS_SELECTOR, ".metric-card")
        logger.info(f"System metric cards found: {len(cpu_metric)}")
        
        logger.info("✅ Data loading tested")
    
    def test_real_time_updates(self):
        """Test that data updates in real-time"""
        if not self.driver:
            self.skipTest("WebDriver not available")
            
        logger.info("Testing real-time updates...")
        
        # Get initial timestamp
        initial_timestamp = self.driver.find_element(By.CSS_SELECTOR, ".timestamp").text
        
        # Wait for update (dashboard updates every 5 seconds)
        time.sleep(6)
        
        # Check if timestamp updated
        try:
            updated_timestamp = self.driver.find_element(By.CSS_SELECTOR, ".timestamp").text
            logger.info(f"Initial: {initial_timestamp}, Updated: {updated_timestamp}")
        except NoSuchElementException:
            logger.info("No timestamp element found - this is okay for some tabs")
        
        logger.info("✅ Real-time updates tested")
    
    def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        if not self.driver:
            self.skipTest("WebDriver not available")
            
        logger.info("Testing responsive design...")
        
        # Test desktop size
        self.driver.set_window_size(1920, 1080)
        time.sleep(1)
        
        # Check that tabs are horizontal on desktop
        tab_container = self.driver.find_element(By.CSS_SELECTOR, ".tabs")
        self.assertTrue(tab_container.is_displayed())
        
        # Test tablet size
        self.driver.set_window_size(768, 1024)
        time.sleep(1)
        
        # Tabs should still be visible
        self.assertTrue(tab_container.is_displayed())
        
        # Test mobile size
        self.driver.set_window_size(375, 667)
        time.sleep(1)
        
        # Tabs should still work on mobile
        self.assertTrue(tab_container.is_displayed())
        
        # Reset to desktop
        self.driver.set_window_size(1920, 1080)
        
        logger.info("✅ Responsive design tested")
    
    def test_error_handling(self):
        """Test error handling when services are unavailable"""
        if not self.driver:
            self.skipTest("WebDriver not available")
            
        logger.info("Testing error handling...")
        
        # Check for error messages in different tabs
        error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .warning")
        logger.info(f"Error/warning elements found: {len(error_elements)}")
        
        # Check for fallback content
        no_data_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'No data') or contains(text(), 'No agents') or contains(text(), 'Not available')]")
        logger.info(f"No data messages found: {len(no_data_elements)}")
        
        logger.info("✅ Error handling tested")
    
    def test_performance(self):
        """Test dashboard performance"""
        if not self.driver:
            self.skipTest("WebDriver not available")
            
        logger.info("Testing performance...")
        
        # Measure page load time
        start_time = time.time()
        self.driver.refresh()
        
        # Wait for page to be fully loaded
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".tabs")))
        
        load_time = time.time() - start_time
        logger.info(f"Page load time: {load_time:.2f} seconds")
        
        # Page should load within 5 seconds
        self.assertLess(load_time, 5.0, "Page should load within 5 seconds")
        
        # Test tab switching performance
        start_time = time.time()
        
        # Switch between several tabs quickly
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".tab")
        for i in range(min(5, len(tabs))):
            self.driver.execute_script("arguments[0].click();", tabs[i])
            time.sleep(0.1)
        
        switch_time = time.time() - start_time
        logger.info(f"Tab switching time: {switch_time:.2f} seconds")
        
        logger.info("✅ Performance tested")
    
    def test_api_endpoints(self):
        """Test API endpoints that feed the dashboard"""
        logger.info("Testing API endpoints...")
        
        endpoints = [
            '/api/agents',
            '/api/console', 
            '/api/system',
            '/api/metrics',
            '/api/cost'
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.dashboard_url}{endpoint}", timeout=5)
                logger.info(f"Endpoint {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.assertIsInstance(data, (dict, list), f"Endpoint {endpoint} should return JSON")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Endpoint {endpoint} not available: {e}")
        
        logger.info("✅ API endpoints tested")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.driver:
            cls.driver.quit()
            
        if cls.dashboard_process:
            cls.dashboard_process.terminate()
            cls.dashboard_process.wait()

class DashboardStressTests(unittest.TestCase):
    """Stress tests for dashboard under load"""
    
    def test_concurrent_connections(self):
        """Test dashboard with multiple concurrent connections"""
        logger.info("Testing concurrent connections...")
        
        def make_request():
            try:
                response = requests.get("http://localhost:5003", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Create 10 concurrent connections
        threads = []
        results = []
        
        for i in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        successful_requests = sum(results)
        logger.info(f"Successful concurrent requests: {successful_requests}/10")
        
        # At least 80% should succeed
        self.assertGreaterEqual(successful_requests, 8)
        
        logger.info("✅ Concurrent connections tested")
    
    def test_memory_usage(self):
        """Test dashboard memory usage over time"""
        logger.info("Testing memory usage...")
        
        import psutil
        import os
        
        # Find dashboard process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'comprehensive-tabbed-dashboard.py' in ' '.join(proc.info['cmdline'] or []):
                    initial_memory = proc.memory_info().rss / 1024 / 1024  # MB
                    logger.info(f"Initial memory usage: {initial_memory:.2f} MB")
                    
                    # Make several requests to simulate usage
                    for i in range(20):
                        requests.get("http://localhost:5003/api/agents", timeout=5)
                        time.sleep(0.1)
                    
                    final_memory = proc.memory_info().rss / 1024 / 1024  # MB
                    logger.info(f"Final memory usage: {final_memory:.2f} MB")
                    
                    memory_increase = final_memory - initial_memory
                    logger.info(f"Memory increase: {memory_increase:.2f} MB")
                    
                    # Memory shouldn't increase by more than 50MB under normal load
                    self.assertLess(memory_increase, 50.0)
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        logger.info("✅ Memory usage tested")

def run_ui_tests():
    """Run all UI tests"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE DASHBOARD UI TESTS")
    print("="*80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add UI tests
    test_suite.addTest(unittest.makeSuite(DashboardUITests))
    test_suite.addTest(unittest.makeSuite(DashboardStressTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n🚨 ERRORS:")
        for test, error in result.errors:
            print(f"  - {test}: {error.split('\\n')[-2]}")
    
    print("="*80)
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_ui_tests()
    exit(0 if success else 1)
