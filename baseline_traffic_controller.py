# =============================================================================
#           BASELINE TRAFFIC CONTROL SYSTEM - ZAMBOANGA KCC
#           REALISTIC BASELINE WITHOUT AI OR 360° DETECTION
#           J1: Basic Fixed-Time Signals | J2: No Traffic Lights (Real-World)
# =============================================================================

import os
import sys
import traci
import csv
from datetime import datetime

# --- Configuration: Set up SUMO environment ---
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# --- Baseline Traffic Controller Class ---
class BaselineTrafficController:
    def __init__(self):
        # BASELINE PARAMETERS - Fixed-time control only
        self.j1_green_ew_time = 45      # Fixed 45-second EW green for J1
        self.j1_green_ns_time = 35      # Fixed 35-second NS green for J1
        self.j1_yellow_time = 5         # Fixed 5-second yellow
        self.j1_red_time = 2            # Fixed 2-second all-red
        
        # Phase timing tracking for J1 only
        self.j1_current_phase = 0       # 0=EW Green, 1=EW Yellow, 2=NS Green, 3=NS Yellow
        self.j1_phase_timer = 0
        self.j1_cycle_start = 0
        
        # Total cycle time for J1
        self.j1_cycle_time = (self.j1_green_ew_time + self.j1_yellow_time + 
                             self.j1_green_ns_time + self.j1_yellow_time + 
                             self.j1_red_time * 2)  # ~92 seconds
        
        # Performance tracking (no AI analysis)
        self.stats = {
            'j1_phase_changes': 0,
            'j1_total_cycle_time': 0,
            'simulation_steps': 0
        }
        
        print("BASELINE CONTROLLER INITIALIZED")
        print(f"   • J1 Cycle Time: {self.j1_cycle_time} seconds")
        print(f"   • J1 EW Green: {self.j1_green_ew_time}s")
        print(f"   • J1 NS Green: {self.j1_green_ns_time}s")
        print("   • J2: NO TRAFFIC LIGHTS (Real-world condition)")
    
    def basic_traffic_control(self, step, tls_j1_id, metrics):
        """Basic fixed-time control for J1 only - no AI, no sensors"""
        
        self.j1_phase_timer += 1
        
        # Determine what phase J1 should be in based on fixed timing
        cycle_position = step % self.j1_cycle_time
        
        # Define phase transitions based on fixed timing
        if cycle_position < self.j1_green_ew_time:
            # EW Green phase
            target_phase = 0
        elif cycle_position < (self.j1_green_ew_time + self.j1_yellow_time):
            # EW Yellow phase
            target_phase = 1
        elif cycle_position < (self.j1_green_ew_time + self.j1_yellow_time + self.j1_red_time):
            # All Red transition
            target_phase = 1  # Keep yellow/red
        elif cycle_position < (self.j1_green_ew_time + self.j1_yellow_time + self.j1_red_time + self.j1_green_ns_time):
            # NS Green phase
            target_phase = 2
        elif cycle_position < (self.j1_green_ew_time + self.j1_yellow_time + self.j1_red_time + self.j1_green_ns_time + self.j1_yellow_time):
            # NS Yellow phase
            target_phase = 3
        else:
            # All Red transition back to EW
            target_phase = 3  # Keep yellow/red
        
        # Apply phase change if needed
        current_phase = traci.trafficlight.getPhase(tls_j1_id)
        if current_phase != target_phase:
            traci.trafficlight.setPhase(tls_j1_id, target_phase)
            self.stats['j1_phase_changes'] += 1
            
            # Log phase changes (less frequent than optimized)
            if step % 180 == 0:  # Every 3 minutes
                print(f"J1 Fixed-time phase: {target_phase} at step {step}")
        
        self.stats['simulation_steps'] = step

# --- Baseline Metrics Collection Class ---
class BaselineMetrics:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_data = []
        self.init_csv_files()
    
    def init_csv_files(self):
        """Initialize CSV files for baseline metrics"""
        with open('baseline_traffic_metrics.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Step', 'Time', 'Vehicles', 'J1_Phase', 'J2_Phase', 
                           'J1_Queue', 'J2_Queue', 'Total_Queue', 'Network_Delay'])
    
    def collect_step_metrics(self, step, tls_j1_id):
        """Collect baseline metrics - no AI analysis"""
        try:
            current_time = step
            total_vehicles = traci.simulation.getMinExpectedNumber()
            j1_phase = traci.trafficlight.getPhase(tls_j1_id)
            j2_phase = -1  # No traffic light at J2
            
            # Calculate basic queue lengths (no 360° detection)
            j1_queue = self.calculate_basic_queue_length('J1')
            j2_queue = self.calculate_basic_queue_length('J2')
            total_queue = j1_queue + j2_queue
            
            # Calculate network delay (simple method)
            network_delay = self.calculate_network_delay()
            
            # Save to CSV
            with open('baseline_traffic_metrics.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([step, current_time, total_vehicles, j1_phase, j2_phase,
                               j1_queue, j2_queue, total_queue, network_delay])
            
        except Exception as e:
            print(f"Baseline metrics collection error: {e}")
    
    def calculate_basic_queue_length(self, intersection):
        """Calculate basic queue length without AI detection"""
        try:
            if intersection == 'J1':
                # Use only main approach detectors for J1
                detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_W1', 'det_J1_W2',
                           'det_J1_N1', 'det_J1_N2', 'det_J1_S1', 'det_J1_S2']
            else:  # J2 - No traffic lights, still count vehicles
                detectors = ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4',
                           'det_J2_W1', 'det_J2_W2', 'det_J2_N1', 'det_J2_N2']
            
            total_halting = 0
            for det in detectors:
                try:
                    total_halting += traci.lanearea.getLastStepHaltingNumber(det)
                except:
                    continue  # Skip if detector doesn't exist
            
            return total_halting
            
        except:
            return 0
    
    def calculate_network_delay(self):
        """Calculate simple network delay"""
        try:
            total_waiting = 0
            vehicle_count = 0
            
            # Get all vehicles in simulation
            for veh_id in traci.vehicle.getIDList():
                waiting_time = traci.vehicle.getWaitingTime(veh_id)
                total_waiting += waiting_time
                vehicle_count += 1
            
            return total_waiting / max(1, vehicle_count)
        except:
            return 0

# --- Main Baseline Simulation Function ---
def run_baseline_simulation():
    """Run the baseline simulation - realistic conditions without AI"""
    
    print("BASELINE SUMO SIMULATION - REAL-WORLD CONDITIONS")
    print("=" * 70)
    print("Features: Fixed-time J1 + No Traffic Lights J2")
    print("Simulation Duration: 500 HOURS (1,800,000 steps)")
    print("Baseline Parameters:")
    print("   • J1: Fixed 45s EW / 35s NS green times")
    print("   • J2: NO TRAFFIC LIGHTS (realistic)")
    print("   • No AI detection or optimization")
    print("   • No 360° camera system")
    print("=" * 70)
    
    # Initialize baseline controller and metrics
    controller = BaselineTrafficController()
    metrics = BaselineMetrics()
    
    # Start SUMO with baseline configuration
    try:
        # Close any existing connections first
        try:
            traci.close()
        except:
            pass
            
        traci.start(["sumo-gui", "-c", "KCCIntersection_baseline.sumocfg", 
                    "--route-files", "KCCIntersection_500h.rou.xml",
                    "--start", "--quit-on-end"])
        print(" Connected to SUMO-GUI with baseline configuration")
    except Exception as e:
        print(f"SUMO startup error: {e}")
        print("Note: If KCCIntersection_baseline.sumocfg doesn't exist, using regular config...")
        try:
            # Close any existing connections first
            try:
                traci.close()
            except:
                pass
                
            traci.start(["sumo-gui", "-c", "KCCIntersection.sumocfg", 
                        "--route-files", "KCCIntersection_500h.rou.xml",
                        "--start", "--quit-on-end"])
            print(" Connected to SUMO-GUI with fallback configuration")
        except Exception as e2:
            print(f"Fallback SUMO startup error: {e2}")
            return

    # Traffic Light IDs
    TLS_ID_J1 = "1017322684"
    # TLS_ID_J2 = "12735512437"  # Available but will be disabled for baseline
    
    # Set J2 to no control (simulating real-world condition)
    TLS_ID_J2 = "12735512437"  # Use actual existing traffic light ID
    try:
        traci.trafficlight.setProgram(TLS_ID_J2, "off")
        print("J2 traffic lights disabled (real-world condition)")
    except:
        print("J2 traffic lights already disabled or don't exist")

    try:
        print("Starting baseline traffic simulation...")
        step = 0
        
        while step < 1800000:  # 500 hours = 1,800,000 steps (continue regardless of vehicle count)
            step += 1
            traci.simulationStep()
            
            # Run baseline traffic control (J1 only)
            controller.basic_traffic_control(step, TLS_ID_J1, metrics)
            
            # Collect metrics every 10 steps
            if step % 10 == 0:
                metrics.collect_step_metrics(step, TLS_ID_J1)
            
            # Progress reporting
            if step % 3600 == 0:  # Every hour
                vehicles = traci.simulation.getMinExpectedNumber()
                j1_phase = traci.trafficlight.getPhase(TLS_ID_J1)
                j1_queue = metrics.calculate_basic_queue_length('J1')
                j2_queue = metrics.calculate_basic_queue_length('J2')
                hour = step // 3600
                print(f"Hour {hour:3d} | Step {step:7d} | Vehicles: {vehicles:3d} | J1 Phase: {j1_phase} | J1 Queue: {j1_queue:2d} | J2 Queue: {j2_queue:2d}")

    except KeyboardInterrupt:
        print("\nBaseline simulation stopped by user")
    except Exception as e:
        print(f"Baseline simulation error: {e}")
    finally:
        traci.close()
        print("\nBASELINE SIMULATION COMPLETE!")
        print("=" * 50)
        print(f"Baseline Performance Summary:")
        print(f"   • J1 Phase changes: {controller.stats['j1_phase_changes']}")
        print(f"   • J2 Control: None (realistic)")
        print(f"   • Simulation duration: {step} steps")
        print(f"Results saved to: baseline_traffic_metrics.csv")

if __name__ == "__main__":
    run_baseline_simulation()