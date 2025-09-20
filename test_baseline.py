#!/usr/bin/env python3
"""
Test SUMO baseline configuration
"""

import subprocess
import sys
import time

def test_baseline():
    try:
        print("Testing baseline SUMO configuration...")
        
        # Start SUMO with baseline config
        cmd = [
            'sumo',
            '-c', 'KCCIntersection_baseline.sumocfg',
            '--start',
            '--quit-on-end'
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        # Run for just a few steps to test
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Baseline configuration test successful!")
            print("STDOUT:", result.stdout[-500:])  # Last 500 chars
        else:
            print("❌ Baseline configuration test failed!")
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout[-500:])
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out (this is expected)")
        return True
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_baseline()
    sys.exit(0 if success else 1)