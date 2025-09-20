#!/usr/bin/env python3
"""
Clean SUMO Traffic Controller - No Early Stopping
"""

import os
import sys
import time
import subprocess

# Add SUMO tools to path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

def kill_existing_sumo():
    """Kill any existing SUMO processes"""
    try:
        # Kill SUMO processes on Windows
        subprocess.run(['taskkill', '/F', '/IM', 'sumo-gui.exe'], 
                      capture_output=True, check=False)
        subprocess.run(['taskkill', '/F', '/IM', 'sumo.exe'], 
                      capture_output=True, check=False)
        time.sleep(1)  # Wait for processes to terminate
    except:
        pass

def clean_traffic_simulation():
    print("🚗 CLEAN TRAFFIC SIMULATION - NO EARLY STOPPING")
    print("=" * 60)
    
    # Kill any existing SUMO processes
    print("Cleaning up existing SUMO processes...")
    kill_existing_sumo()
    
    # Close any existing TraCI connections
    try:
        traci.close()
    except:
        pass
    
    # Wait a moment
    time.sleep(2)
    
    try:
        # Start SUMO with the working configuration
        print("Starting SUMO with clean configuration...")
        
        traci.start([
            "sumo-gui", 
            "-c", "KCCIntersection_optimized.sumocfg",
            "--step-length", "1",
            "--start"
        ])
        
        print("✅ SUMO started successfully!")
        
        # Get traffic light information
        available_tls = traci.trafficlight.getIDList()
        print(f"Available traffic lights: {available_tls}")
        
        TLS_ID_J1 = "1017322684" if "1017322684" in available_tls else None
        TLS_ID_J2 = "1017322720" if "1017322720" in available_tls else None
        
        if not TLS_ID_J1:
            print("❌ J1 traffic light not found!")
            return
        
        print(f"✅ J1 Traffic Light: {TLS_ID_J1}")
        print(f"{'✅' if TLS_ID_J2 else '⚠️'} J2 Traffic Light: {TLS_ID_J2 or 'Not Found'}")
        
        # Run simulation for specified duration (test with 30 minutes first)
        test_duration = 1800  # 30 minutes = 1800 seconds
        print(f"\nRunning simulation for {test_duration//60} minutes...")
        
        vehicles_seen = set()
        j1_phase_changes = 0
        j2_phase_changes = 0
        last_j1_phase = traci.trafficlight.getPhase(TLS_ID_J1)
        last_j2_phase = traci.trafficlight.getPhase(TLS_ID_J2) if TLS_ID_J2 else -1
        
        for step in range(1, test_duration + 1):
            try:
                traci.simulationStep()
                
                # Get current vehicles
                current_vehicles = traci.vehicle.getIDList()
                vehicles_seen.update(current_vehicles)
                
                # Simple adaptive traffic control
                if step % 60 == 0:  # Check every minute
                    # Get traffic data (simplified)
                    active = len(current_vehicles)
                    expected = traci.simulation.getMinExpectedNumber()
                    
                    # J1 Control: Switch between EW and NS every 60 seconds
                    current_j1_phase = traci.trafficlight.getPhase(TLS_ID_J1)
                    if current_j1_phase != last_j1_phase:
                        j1_phase_changes += 1
                        last_j1_phase = current_j1_phase
                    
                    # Simple phase switching
                    cycle_pos = (step // 60) % 2
                    target_phase = 0 if cycle_pos == 0 else 2  # EW or NS
                    if current_j1_phase != target_phase:
                        traci.trafficlight.setPhase(TLS_ID_J1, target_phase)
                        j1_phase_changes += 1
                        phase_name = "EW" if target_phase == 0 else "NS"
                        print(f"    J1 Phase → {phase_name} at step {step}")
                    
                    # J2 Control (if available)
                    if TLS_ID_J2:
                        current_j2_phase = traci.trafficlight.getPhase(TLS_ID_J2)
                        if current_j2_phase != last_j2_phase:
                            j2_phase_changes += 1
                            last_j2_phase = current_j2_phase
                
                # Progress reporting every 5 minutes
                if step % 300 == 0:
                    active = len(current_vehicles)
                    expected = traci.simulation.getMinExpectedNumber()
                    minute = step // 60
                    j1_phase = traci.trafficlight.getPhase(TLS_ID_J1)
                    
                    print(f"  Minute {minute:2d} | Step {step:4d} | Active: {active:2d} | Expected: {expected:2d} | J1 Phase: {j1_phase}")
                    
                    if current_vehicles:
                        sample_vehicles = list(current_vehicles)[:3]
                        print(f"           Sample vehicles: {sample_vehicles}")
                
            except traci.exceptions.FatalTraCIError as e:
                print(f"  ⚠️  TraCI Fatal Error at step {step}: {e}")
                print("  Simulation may have ended naturally")
                break
            except Exception as e:
                print(f"  ❌ Error at step {step}: {e}")
                break
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"   Duration: {step} steps ({step//60} minutes)")
        print(f"   Total unique vehicles: {len(vehicles_seen)}")
        print(f"   Final active vehicles: {len(traci.vehicle.getIDList())}")
        print(f"   J1 phase changes: {j1_phase_changes}")
        print(f"   J2 phase changes: {j2_phase_changes}")
        
        if len(vehicles_seen) > 0:
            print("✅ SUCCESS! Traffic simulation completed with visible cars!")
            print(f"   Vehicles seen: {list(vehicles_seen)[:10]}")
        else:
            print("❌ No vehicles appeared in simulation")
        
        traci.close()
        print("✅ Simulation ended cleanly")
        
    except KeyboardInterrupt:
        print("\n⚠️  Simulation stopped by user")
        try:
            traci.close()
        except:
            pass
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    clean_traffic_simulation()