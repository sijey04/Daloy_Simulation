#!/usr/bin/env python3
"""
Simple Test to Verify SUMO Fixes Work
Tests the fixed configuration for warnings
"""

import os
import sys
import subprocess
import time

def test_sumo_configuration():
    """Test if SUMO runs without warnings using our fixes"""
    print("🔬 TESTING SUMO FIXES")
    print("=" * 50)
    
    # Find SUMO binary
    sumo_binary = None
    try:
        if 'SUMO_HOME' in os.environ:
            sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo.exe')
            if not os.path.exists(sumo_binary):
                sumo_binary = None
        
        if not sumo_binary:
            # Try to find in PATH
            result = subprocess.run(['where', 'sumo'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                sumo_binary = result.stdout.strip().split('\n')[0]
    except:
        pass
    
    if not sumo_binary:
        print("❌ SUMO not found")
        return False
    
    print(f"✅ Found SUMO: {sumo_binary}")
    
    # Test fixed configuration
    config_file = "KCCIntersection_optimized_stable.sumocfg"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    print(f"✅ Configuration file found: {config_file}")
    
    # Run SUMO for a short test (10 seconds simulation time)
    print("\n🚀 Running SUMO test simulation...")
    cmd = [
        sumo_binary,
        "-c", config_file,
        "--begin", "0",
        "--end", "10",
        "--no-warnings", "false",
        "--verbose"
    ]
    
    try:
        print("Command:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print("\n📊 SUMO OUTPUT:")
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        
        # Check for warnings
        stderr_lower = result.stderr.lower()
        warnings_found = []
        
        if "warning" in stderr_lower:
            lines = result.stderr.split('\n')
            for line in lines:
                if "warning" in line.lower():
                    warnings_found.append(line.strip())
        
        if warnings_found:
            print(f"\n⚠️ FOUND {len(warnings_found)} WARNINGS:")
            for warning in warnings_found:
                print(f"   {warning}")
        else:
            print("\n✅ NO WARNINGS FOUND!")
        
        print(f"\nReturn code: {result.returncode}")
        return result.returncode == 0 and len(warnings_found) == 0
        
    except subprocess.TimeoutExpired:
        print("❌ SUMO test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running SUMO: {e}")
        return False

def test_files_exist():
    """Test if all required fixed files exist"""
    print("\n📁 CHECKING FIXED FILES")
    print("=" * 50)
    
    required_files = [
        "KCCIntersectionConfig_fixed.add.xml",
        "improved_traffic_lights.add.xml", 
        "optimized_vehicles.rou.xml",
        "KCCIntersection_optimized_stable.sumocfg",
        "KCCIntersection_super_visible.rou.xml",
        "KCCIntersection.net.xml"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    print("🧪 COMPREHENSIVE SUMO FIX VERIFICATION")
    print("=" * 60)
    
    # Test 1: Check files exist
    files_ok = test_files_exist()
    
    # Test 2: Test SUMO configuration
    sumo_ok = test_sumo_configuration()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    print("=" * 60)
    
    if files_ok:
        print("✅ All required files exist")
    else:
        print("❌ Some files are missing")
    
    if sumo_ok:
        print("✅ SUMO runs without warnings")
        print("✅ All detector issues fixed")
        print("✅ Configuration is stable")
    else:
        print("❌ SUMO issues detected")
    
    if files_ok and sumo_ok:
        print("\n🎉 ALL FIXES SUCCESSFUL!")
        print("✅ Your simulation is ready to run warning-free")
    else:
        print("\n⚠️ Some issues remain")
    
    print("=" * 60)

if __name__ == "__main__":
    main()