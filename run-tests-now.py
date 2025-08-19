#!/usr/bin/env python3
"""Auto-generated test runner for Playwright tests"""
import os
import subprocess
from pathlib import Path

def run_service_tests(service_path, test_dir="mfe/tests"):
    """Run Playwright tests for a service"""
    full_path = Path(service_path) / test_dir
    if not full_path.exists():
        return False
        
    os.chdir(service_path)
    
    # Install dependencies if needed
    if not Path("node_modules").exists():
        print(f"Installing dependencies for {service_path}...")
        subprocess.run(["npm", "install"], capture_output=True)
    
    # Run tests
    print(f"Running Playwright tests in {service_path}/{test_dir}...")
    result = subprocess.run(
        ["npx", "playwright", "test", "--reporter=list"],
        capture_output=False
    )
    
    return result.returncode == 0

# Services to test
services = [
    ("E:/Projects/VisualForgeMediaV2/vf-dashboard-service", "mfe/tests"),
    ("E:/Projects/VisualForgeMediaV2/vf-audio-service", "mfe/tests"),
    ("E:/Projects/VisualForgeMediaV2/vf-video-service", "mfe/tests"),
    ("E:/Projects/NiroSubs-V2/ns-shell", "tests")
]

print("[TEST RUNNER] Starting Playwright test execution")
for service_path, test_dir in services:
    if Path(service_path).exists():
        print(f"\nTesting {service_path}...")
        success = run_service_tests(service_path, test_dir)
        if not success:
            print(f"[FAILED] Tests failed for {service_path}")
            # Create bug issue
            subprocess.run([
                "gh", "issue", "create",
                "--repo", "VisualForgeMediaV2/business-operations",
                "--title", f"[BUG] Test failures in {Path(service_path).name}",
                "--body", f"Playwright tests failed in {service_path}\nRequires immediate fix",
                "--label", "bug,testing,priority/P1"
            ])
