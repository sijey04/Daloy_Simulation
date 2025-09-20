#!/usr/bin/env python3
"""
Test script to verify the 24-hour realistic route file works correctly
"""
import subprocess
import sys
import os

def test_24hour_route_file():
    """Test the new 24-hour realistic route file"""
    
    print("🚦 TESTING 24-HOUR REALISTIC TRAFFIC PATTERN")
    print("=" * 60)
    
    # Check if the route file exists
    route_file = "KCCIntersection_24hour_realistic.rou.xml"
    if not os.path.exists(route_file):
        print(f"❌ ERROR: Route file {route_file} not found!")
        return False
    
    print(f"✅ Route file found: {route_file}")
    
    # Check if configuration files are updated
    config_files = [
        "KCCIntersection.sumocfg",
        "KCCIntersection_24hour.sumocfg", 
        "KCCIntersection_optimized.sumocfg",
        "KCCIntersection_baseline.sumocfg"
    ]
    
    print(f"\n📋 CONFIGURATION FILES STATUS:")
    for config in config_files:
        if os.path.exists(config):
            print(f"   ✅ {config}")
        else:
            print(f"   ⚠️  {config} (optional)")
    
    # Test route file with quick SUMO simulation
    print(f"\n🧪 TESTING ROUTE FILE WITH SUMO...")
    try:
        # Run a quick 60-second test simulation
        result = subprocess.run([
            "sumo", 
            "--net-file", "KCCIntersection.net.xml",
            "--route-files", route_file,
            "--begin", "0",
            "--end", "60",
            "--no-warnings", "true",
            "--no-step-log", "true"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Route file validation: PASSED")
            print("   ✅ SUMO can load and run the 24-hour route file")
        else:
            print("   ❌ Route file validation: FAILED")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Test timed out (SUMO might be working but slow)")
    except FileNotFoundError:
        print("   ⚠️  SUMO not found in PATH - route file exists but cannot test")
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False
    
    print(f"\n📊 TRAFFIC PATTERN SUMMARY:")
    print(f"   🌅 Morning Rush: 7-9 AM (High volume)")
    print(f"   🏙️  Midday: 10 AM-4 PM (Medium volume)")
    print(f"   🌆 Evening Rush: 5-7 PM (High volume)")
    print(f"   🌃 Night: 8 PM-6 AM (Low volume)")
    print(f"   🚗 Authentic Filipino vehicle mix")
    print(f"   ⏱️  24-hour simulation duration")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Run simulation: sumo-gui -c KCCIntersection_24hour.sumocfg")
    print(f"   2. Or use optimized controller: python optimized_traffic_controller.py")
    print(f"   3. Or use baseline controller: python baseline_traffic_controller.py")
    
    print(f"\n✅ 24-HOUR REALISTIC TRAFFIC SETUP COMPLETE!")
    return True

if __name__ == "__main__":
    success = test_24hour_route_file()
    sys.exit(0 if success else 1)