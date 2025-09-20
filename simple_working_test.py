#!/usr/bin/env python3
"""
Simple Working Traffic Controller Test
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

def simple_working_test():
    print("🚗 SIMPLE WORKING TRAFFIC CONTROLLER TEST")
    print("=" * 60)
    
    try:
        # Close any existing connections
        try:
            traci.close()
        except:
            pass
        
        # Start SUMO with minimal configuration
        print("Starting SUMO...")
        traci.start([
            "sumo-gui", 
            "-c", "KCCIntersection_optimized_fixed.sumocfg"
        ])
        
        print("✅ SUMO started successfully!")
        
        # Get traffic light IDs
        available_tls = traci.trafficlight.getIDList()
        print(f"Available traffic lights: {available_tls}")
        
        TLS_ID_J1 = "1017322684" if "1017322684" in available_tls else None
        TLS_ID_J2 = "1017322720" if "1017322720" in available_tls else None
        
        print(f"J1 Traffic Light: {'Found' if TLS_ID_J1 else 'Not Found'}")
        print(f"J2 Traffic Light: {'Found' if TLS_ID_J2 else 'Not Found'}")
        
        # Run simulation for 10 minutes (600 steps)
        print("\nRunning simulation for 10 minutes...")
        vehicles_seen = set()
        
        for step in range(600):
            try:
                traci.simulationStep()
                
                # Get current vehicles
                current_vehicles = traci.vehicle.getIDList()
                vehicles_seen.update(current_vehicles)
                
                # Report every minute
                if step % 60 == 0:
                    active = len(current_vehicles)
                    expected = traci.simulation.getMinExpectedNumber()
                    minute = step // 60
                    print(f"  Minute {minute:2d} | Step {step:3d} | Active: {active:2d} | Expected: {expected:2d}")
                    
                    # Show some vehicle IDs if available
                    if current_vehicles:
                        print(f"           Vehicles: {list(current_vehicles)[:3]}")
                
                # Basic traffic light control
                if TLS_ID_J1:
                    # Simple 60-second cycle: 30s EW, 30s NS
                    cycle_pos = step % 60
                    if cycle_pos < 30:
                        traci.trafficlight.setPhase(TLS_ID_J1, 0)  # EW green
                    else:
                        traci.trafficlight.setPhase(TLS_ID_J1, 2)  # NS green
                
            except Exception as e:
                print(f"  ❌ Error at step {step}: {e}")
                break
        
        print(f"\n🎯 SIMULATION RESULTS:")
        print(f"   Completed steps: {step}")
        print(f"   Total unique vehicles seen: {len(vehicles_seen)}")
        print(f"   Final active vehicles: {len(traci.vehicle.getIDList())}")
        
        if len(vehicles_seen) > 0:
            print("✅ SUCCESS! Traffic simulation is working with visible cars!")
            print(f"   Vehicle IDs seen: {list(vehicles_seen)[:10]}")
        else:
            print("❌ No vehicles appeared in simulation")
        
        traci.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    simple_working_test()