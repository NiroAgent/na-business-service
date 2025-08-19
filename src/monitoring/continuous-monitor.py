#!/usr/bin/env python3
import subprocess
import time
import json
from datetime import datetime

print("\n" + "="*80)
print("AUTONOMOUS MONITORING SYSTEM ACTIVE")
print("="*80)
print(f"Started at: {datetime.now()}")
print("Monitoring all agent activities...")
print("\nThis system will run continuously until all tasks are complete.")
print("="*80)

while True:
    try:
        # Run the coordinator
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running coordination cycle...")
        
        result = subprocess.run([
            "python", "agent-policy-coordinator.py", "--once"
        ], capture_output=True, text=True, timeout=120)
        
        # Check for issues
        if "Found 0 open issues" in result.stdout:
            print("[OK] All issues processed! System complete.")
            break
        elif "Found" in result.stdout and "issues" in result.stdout:
            # Extract issue count
            import re
            match = re.search(r"Found (\d+) open issues", result.stdout)
            if match:
                count = match.group(1)
                print(f"  [LIST] {count} issues remaining")
        
        # Check agent status
        print("  [ROBOT] Agents active and processing...")
        
        # Wait before next cycle
        print("  [CLOCK] Next check in 60 seconds...")
        time.sleep(60)
        
    except subprocess.TimeoutExpired:
        print("  [WARN] Coordinator timeout, retrying...")
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        break
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        time.sleep(30)

print("\n" + "="*80)
print("MONITORING COMPLETE")
print("="*80)
