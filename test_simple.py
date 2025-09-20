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

def test_simple():
    """Simple test without complex logic"""
    
    print("Simple SUMO test...")
    
    try:
        # Start SUMO with minimal configuration
        print("Starting SUMO...")
        traci.start(["sumo", 
                    "--net-file", "KCCIntersection.net.xml",
                    "--route-files", "KCCIntersection_500h.rou.xml",
                    "--start", "--quit-on-end"])
        
        print("SUMO started successfully!")
        
        # Get traffic light list
        tls_list = traci.trafficlight.getIDList()
        print(f"Traffic lights found: {tls_list}")
        
        # Take one simulation step
        traci.simulationStep()
        print("Simulation step completed!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        
    finally:
        try:
            traci.close()
            print("SUMO closed successfully")
        except:
            print("SUMO was already closed")

if __name__ == "__main__":
    test_simple()