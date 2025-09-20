#!/usr/bin/env python3
"""
Simple SUMO Test with New Route
"""

import os
import sys

# Add SUMO tools to path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

def simple_test():
    print("🚗 SIMPLE SUMO TEST WITH NEW ROUTE")
    print("=" * 50)
    
    try:
        # Close any existing connections
        try:
            traci.close()
        except:
            pass
            
        # Start SUMO with simple configuration
        traci.start(["sumo-gui", "-c", "KCCIntersection_optimized.sumocfg", 
                    "--start", "--quit-on-end"])
        
        print("✅ SUMO started successfully")
        
        # Run for 10 steps and check vehicles
        vehicles_seen = set()
        for step in range(30):
            traci.simulationStep()
            
            # Get current vehicles
            current_vehicles = traci.vehicle.getIDList()
            vehicles_seen.update(current_vehicles)
            
            if step % 5 == 0:
                print(f"   Step {step:2d}: {len(current_vehicles)} active vehicles")
                if current_vehicles:
                    print(f"             IDs: {list(current_vehicles)[:5]}")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total unique vehicles seen: {len(vehicles_seen)}")
        print(f"   Vehicle IDs: {list(vehicles_seen)[:10]}")
        
        if len(vehicles_seen) > 0:
            print("✅ SUCCESS! Cars are now visible in simulation!")
        else:
            print("❌ Still no cars visible")
        
        traci.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    simple_test()