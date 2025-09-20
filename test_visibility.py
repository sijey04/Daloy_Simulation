#!/usr/bin/env python3
"""
Quick Test to Verify Cars Are Now Visible
"""

import os
import sys
import subprocess
import time

# Add SUMO tools to path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

def quick_visibility_test():
    print("🚗 QUICK VISIBILITY TEST")
    print("=" * 50)
    print("Testing new super visible route file...")
    
    try:
        # Start SUMO with the new route file
        traci.start(["sumo-gui", "-c", "KCCIntersection_optimized.sumocfg", 
                    "--start", "--quit-on-end", "--step-length", "1"])
        
        print("✅ SUMO started successfully")
        
        # Test for first 60 seconds
        for step in range(60):
            traci.simulationStep()
            
            # Get vehicle count
            vehicle_count = len(traci.vehicle.getIDList())
            vehicles = traci.vehicle.getIDList()
            
            # Report every 10 seconds
            if step % 10 == 0:
                print(f"   Step {step:2d}: {vehicle_count} vehicles - {vehicles[:3] if vehicles else 'None'}")
            
            # Check if we have vehicles
            if vehicle_count > 0:
                print(f"🎉 SUCCESS! Cars are visible at step {step}")
                print(f"   Active vehicles: {vehicles}")
                break
        
        else:
            print("❌ No vehicles appeared in first 60 seconds")
        
        traci.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    quick_visibility_test()