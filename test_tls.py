#!/usr/bin/env python3

import os
import sys
import traci

# Set up SUMO environment
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

def test_traffic_lights():
    """Test what traffic lights are available"""
    
    print("Testing SUMO traffic light configuration...")
    print("=" * 50)
    
    try:
        # Start SUMO
        print("Starting SUMO...")
        traci.start(["sumo", "-c", "KCCIntersection_optimized.sumocfg", "--start", "--quit-on-end"])
        
        # Get traffic light list
        print("Querying traffic lights...")
        tls_list = traci.trafficlight.getIDList()
        
        print(f"Found {len(tls_list)} traffic lights:")
        for i, tls in enumerate(tls_list, 1):
            print(f"  {i}. {tls}")
        
        # Check our target IDs
        target_j1 = "1017322684"
        target_j2 = "1017322720"
        
        print(f"\nChecking target traffic lights:")
        print(f"  J1 ({target_j1}): {'✓ FOUND' if target_j1 in tls_list else '✗ NOT FOUND'}")
        print(f"  J2 ({target_j2}): {'✓ FOUND' if target_j2 in tls_list else '✗ NOT FOUND'}")
        
        # Test accessing each found traffic light
        print(f"\nTesting traffic light access:")
        for tls in tls_list:
            try:
                phase = traci.trafficlight.getPhase(tls)
                print(f"  {tls}: Phase {phase} ✓")
            except Exception as e:
                print(f"  {tls}: ERROR - {e}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        
    finally:
        try:
            traci.close()
            print("\nSUMO connection closed successfully")
        except:
            print("\nSUMO was already closed")

if __name__ == "__main__":
    test_traffic_lights()