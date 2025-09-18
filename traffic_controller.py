# =============================================================================
#           SMART TRAFFIC CONTROL SYSTEM - ZAMBOANGA KCC
# =============================================================================

import os
import sys
import traci  # The SUMO TraCI library
import csv
import time
from datetime import datetime

# --- Configuration: Set up SUMO environment ---
# This ensures the script can find the SUMO tools
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# --- Metrics Collection Class ---
class TrafficMetrics:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_data = []
        self.vehicle_data = {}  # Store individual vehicle information
        self.intersection_stats = {
            'J1': {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0},
            'J2': {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0}
        }
        
        # Initialize CSV files for detailed logging
        self.init_csv_files()
    
    def init_csv_files(self):
        """Initialize CSV files for different metrics"""
        # Main metrics file
        with open('traffic_metrics.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Simulation_Step', 'Timestamp', 'Total_Vehicles', 'Average_Speed',
                'J1_Queue_Length', 'J2_Queue_Length', 'J1_Current_Phase', 'J2_Current_Phase',
                'J1_Waiting_Time', 'J2_Waiting_Time', 'Total_CO2', 'Total_NOx', 'Total_PMx',
                'J1_Throughput', 'J2_Throughput'
            ])
        
        # Vehicle details file
        with open('vehicle_details.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Vehicle_ID', 'Entry_Time', 'Exit_Time', 'Travel_Time', 'Route_Length',
                'Average_Speed', 'Total_Waiting_Time', 'CO2_Emission', 'NOx_Emission', 'PMx_Emission'
            ])
        
        # Intersection summary file
        with open('intersection_summary.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Hour', 'J1_Total_Vehicles', 'J1_Avg_Delay', 'J1_Avg_Queue', 'J1_Phase_Changes',
                'J2_Total_Vehicles', 'J2_Avg_Delay', 'J2_Avg_Queue', 'J2_Phase_Changes',
                'Total_Emissions_CO2', 'Total_Emissions_NOx', 'Total_Emissions_PMx'
            ])
    
    def collect_step_metrics(self, step, tls_j1_id, tls_j2_id):
        """Collect metrics for current simulation step"""
        try:
            # Basic simulation metrics
            vehicle_ids = traci.vehicle.getIDList()
            total_vehicles = len(vehicle_ids)
            
            # Calculate average speed
            avg_speed = 0
            total_waiting_time_j1 = 0
            total_waiting_time_j2 = 0
            total_co2 = 0
            total_nox = 0
            total_pmx = 0
            
            if total_vehicles > 0:
                speeds = [traci.vehicle.getSpeed(veh_id) for veh_id in vehicle_ids]
                avg_speed = sum(speeds) / len(speeds)
                
                # Collect emissions data
                for veh_id in vehicle_ids:
                    total_co2 += traci.vehicle.getCO2Emission(veh_id)
                    total_nox += traci.vehicle.getNOxEmission(veh_id)
                    total_pmx += traci.vehicle.getPMxEmission(veh_id)
                    
                    # Track vehicle entry times
                    if veh_id not in self.vehicle_data:
                        self.vehicle_data[veh_id] = {
                            'entry_time': step,
                            'total_co2': 0,
                            'total_nox': 0,
                            'total_pmx': 0,
                            'total_waiting': 0
                        }
                    
                    # Update vehicle emissions
                    self.vehicle_data[veh_id]['total_co2'] += traci.vehicle.getCO2Emission(veh_id)
                    self.vehicle_data[veh_id]['total_nox'] += traci.vehicle.getNOxEmission(veh_id)
                    self.vehicle_data[veh_id]['total_pmx'] += traci.vehicle.getPMxEmission(veh_id)
                    self.vehicle_data[veh_id]['total_waiting'] += traci.vehicle.getWaitingTime(veh_id)
            
            # Queue lengths using detectors
            j1_queue = self.calculate_queue_length('J1')
            j2_queue = self.calculate_queue_length('J2')
            
            # Traffic light phases
            j1_phase = traci.trafficlight.getPhase(tls_j1_id)
            j2_phase = traci.trafficlight.getPhase(tls_j2_id)
            
            # Waiting times at intersections
            j1_waiting = self.calculate_intersection_waiting_time('J1')
            j2_waiting = self.calculate_intersection_waiting_time('J2')
            
            # Throughput (vehicles passing through per hour)
            j1_throughput = self.calculate_throughput('J1', step)
            j2_throughput = self.calculate_throughput('J2', step)
            
            # Store metrics
            metrics_row = [
                step, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), total_vehicles, avg_speed,
                j1_queue, j2_queue, j1_phase, j2_phase, j1_waiting, j2_waiting,
                total_co2, total_nox, total_pmx, j1_throughput, j2_throughput
            ]
            
            # Write to CSV every 100 steps to avoid performance issues
            if step % 100 == 0:
                with open('traffic_metrics.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(metrics_row)
            
            return metrics_row
            
        except Exception as e:
            print(f"Error collecting metrics at step {step}: {e}")
            return None
    
    def calculate_queue_length(self, intersection):
        """Calculate queue length for intersection using halting vehicle count"""
        try:
            if intersection == 'J1':
                detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4',
                           'det_J1_W1', 'det_J1_W2', 'det_J1_N1', 'det_J1_N2',
                           'det_J1_N3', 'det_J1_N4', 'det_J1_S1', 'det_J1_S2',
                           'det_J1_S3', 'det_J1_S4']
            else:  # J2
                detectors = ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4',
                           'det_J2_E5', 'det_J2_E6', 'det_J2_W1', 'det_J2_W2',
                           'det_J2_W3', 'det_J2_W4', 'det_J2_N1', 'det_J2_N2',
                           'det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4']
            
            total_halting = 0
            for det_id in detectors:
                total_halting += traci.lanearea.getLastStepHaltingNumber(det_id)
            
            return total_halting
        except:
            return 0
    
    def calculate_intersection_waiting_time(self, intersection):
        """Calculate average waiting time for vehicles near intersection"""
        try:
            if intersection == 'J1':
                detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4',
                           'det_J1_W1', 'det_J1_W2', 'det_J1_N1', 'det_J1_N2',
                           'det_J1_N3', 'det_J1_N4', 'det_J1_S1', 'det_J1_S2',
                           'det_J1_S3', 'det_J1_S4']
            else:  # J2
                detectors = ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4',
                           'det_J2_E5', 'det_J2_E6', 'det_J2_W1', 'det_J2_W2',
                           'det_J2_W3', 'det_J2_W4', 'det_J2_N1', 'det_J2_N2',
                           'det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4']
            
            total_waiting = 0
            vehicle_count = 0
            
            for det_id in detectors:
                vehicles = traci.lanearea.getLastStepVehicleIDs(det_id)
                for veh_id in vehicles:
                    total_waiting += traci.vehicle.getWaitingTime(veh_id)
                    vehicle_count += 1
            
            return total_waiting / vehicle_count if vehicle_count > 0 else 0
        except:
            return 0
    
    def calculate_throughput(self, intersection, step):
        """Calculate vehicles per hour throughput"""
        # This is a simplified calculation - in practice you'd track vehicles passing through
        try:
            if intersection == 'J1':
                detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_W1', 'det_J1_W2']
            else:  # J2
                detectors = ['det_J2_E1', 'det_J2_E2', 'det_J2_W1', 'det_J2_W2']
            
            total_vehicles = 0
            for det_id in detectors:
                total_vehicles += traci.lanearea.getLastStepVehicleNumber(det_id)
            
            # Convert to vehicles per hour (rough approximation)
            return total_vehicles * 3600 / max(step, 1)
        except:
            return 0
    
    def log_vehicle_completion(self, veh_id, exit_time):
        """Log completed vehicle journey"""
        if veh_id in self.vehicle_data:
            vehicle_info = self.vehicle_data[veh_id]
            travel_time = exit_time - vehicle_info['entry_time']
            
            try:
                route_length = traci.vehicle.getDistance(veh_id)
                avg_speed = route_length / travel_time if travel_time > 0 else 0
                
                # Write to vehicle details CSV
                with open('vehicle_details.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        veh_id, vehicle_info['entry_time'], exit_time, travel_time,
                        route_length, avg_speed, vehicle_info['total_waiting'],
                        vehicle_info['total_co2'], vehicle_info['total_nox'], 
                        vehicle_info['total_pmx']
                    ])
                
                # Remove from tracking
                del self.vehicle_data[veh_id]
            except:
                pass
    
    def save_hourly_summary(self, hour, tls_j1_id, tls_j2_id):
        """Save hourly summary statistics"""
        try:
            # Calculate hourly statistics
            j1_stats = self.intersection_stats['J1']
            j2_stats = self.intersection_stats['J2']
            
            # Get current emissions totals
            total_co2 = sum(data.get('total_co2', 0) for data in self.vehicle_data.values())
            total_nox = sum(data.get('total_nox', 0) for data in self.vehicle_data.values())
            total_pmx = sum(data.get('total_pmx', 0) for data in self.vehicle_data.values())
            
            with open('intersection_summary.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    hour,
                    j1_stats['total_vehicles'], 
                    j1_stats['total_delay'] / max(j1_stats['total_vehicles'], 1),
                    self.calculate_queue_length('J1'),
                    j1_stats['phase_changes'],
                    j2_stats['total_vehicles'],
                    j2_stats['total_delay'] / max(j2_stats['total_vehicles'], 1),
                    self.calculate_queue_length('J2'),
                    j2_stats['phase_changes'],
                    total_co2, total_nox, total_pmx
                ])
            
            # Reset hourly counters
            self.intersection_stats['J1'] = {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0}
            self.intersection_stats['J2'] = {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0}
            
        except Exception as e:
            print(f"Error saving hourly summary: {e}")
    
    def finalize_metrics(self):
        """Generate final summary report"""
        print(f"\n{'='*60}")
        print("TRAFFIC SIMULATION COMPLETE - 200 HOURS")
        print(f"{'='*60}")
        print(f"Simulation started: {self.start_time}")
        print(f"Simulation ended: {datetime.now()}")
        print(f"Duration: {datetime.now() - self.start_time}")
        print(f"\nMetrics files generated:")
        print(f"  - traffic_metrics.csv (detailed step-by-step data)")
        print(f"  - vehicle_details.csv (individual vehicle journeys)")
        print(f"  - intersection_summary.csv (hourly summaries)")
        print(f"{'='*60}")

# --- Main Simulation Function ---
def run_simulation():
    """Executes the TraCI control loop for the smart traffic system with comprehensive metrics."""

    # Initialize metrics collection
    metrics = TrafficMetrics()
    
    # Start the SUMO simulation with the GUI and connect our script to it
    try:
        traci.start(["sumo-gui", "-c", "KCCIntersection.sumocfg", "--start"])
        print("SUMO simulation started successfully!")
        print("Starting 200-hour traffic simulation with comprehensive metrics collection...")
        print("Metrics will be saved to: traffic_metrics.csv, vehicle_details.csv, intersection_summary.csv")
    except Exception as e:
        print(f"Error starting SUMO: {e}")
        return

    # --- Your Custom IDs from Netedit ---
    TLS_ID_J1 = "1017322684"  # The ID of the complex intersection on the left
    TLS_ID_J2 = "1017322720"  # The ID of the 4-way intersection on the right
    
    # Track previous phases for phase change detection
    prev_j1_phase = traci.trafficlight.getPhase(TLS_ID_J1)
    prev_j2_phase = traci.trafficlight.getPhase(TLS_ID_J2)

    try:
        # --- Main Simulation Loop ---
        # This loop continues as long as there are cars in the simulation
        step = 0
        max_steps = 720000  # Maximum simulation time (200 hours)
        
        while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
            
            traci.simulationStep()  # Advance the simulation by one second
            step += 1

            # Print progress every 3600 steps (1 hour)
            if step % 3600 == 0:
                hours = step // 3600
                print(f"Simulation hour: {hours}/200 ({hours/200*100:.1f}% complete)")
                # Save hourly summary
                metrics.save_hourly_summary(hours, TLS_ID_J1, TLS_ID_J2)

            # Collect metrics every step
            metrics.collect_step_metrics(step, TLS_ID_J1, TLS_ID_J2)

            # --- AI LOGIC FOR INTERSECTION 1 (The Complex One) ---
            
            # Get data from the "360-camera" by reading our detectors
            # We use the segmented detector strategy: add the parts together for a total count
            
            try:
                # West Approach (from far left)
                # IMPORTANT: Replace with your actual detector names if they are different
                cars_J1_W = traci.lanearea.getLastStepHaltingNumber("det_J1_W1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_W2")

                # East Approach (the road between the two intersections)
                cars_J1_E = traci.lanearea.getLastStepHaltingNumber("det_J1_E1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_E2") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_E3") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_E4")

                # North Approach
                cars_J1_N = traci.lanearea.getLastStepHaltingNumber("det_J1_N1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_N2") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_N3") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_N4")
                
                # South Approach
                cars_J1_S = traci.lanearea.getLastStepHaltingNumber("det_J1_S1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_S2") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_S3") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J1_S4")

                # Simple AI Logic: Find the busiest direction for Intersection 1
                if (cars_J1_E + cars_J1_W) > (cars_J1_N + cars_J1_S):
                    # East-West is busier, set its lights to green (Phase 0 is usually the main direction)
                    if traci.trafficlight.getPhase(TLS_ID_J1) != 0:
                        traci.trafficlight.setPhase(TLS_ID_J1, 0)
                        # Track phase change
                        if prev_j1_phase != 0:
                            metrics.intersection_stats['J1']['phase_changes'] += 1
                        prev_j1_phase = 0
                else:
                    # North-South is busier, set its lights to green (Phase 2 is usually the secondary direction)
                    if traci.trafficlight.getPhase(TLS_ID_J1) != 2:
                        traci.trafficlight.setPhase(TLS_ID_J1, 2)
                        # Track phase change
                        if prev_j1_phase != 2:
                            metrics.intersection_stats['J1']['phase_changes'] += 1
                        prev_j1_phase = 2

                # --- AI LOGIC FOR INTERSECTION 2 (The 4-Way One) ---
                
                cars_J2_W = traci.lanearea.getLastStepHaltingNumber("det_J2_W1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_W2") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_W3") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_W4")
                
                cars_J2_E = traci.lanearea.getLastStepHaltingNumber("det_J2_E1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_E2") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_E3") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_E4") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_E5") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_E6")

                cars_J2_N = traci.lanearea.getLastStepHaltingNumber("det_J2_N1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_N2")

                cars_J2_S = traci.lanearea.getLastStepHaltingNumber("det_J2_S1") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_S2") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_S3") + \
                            traci.lanearea.getLastStepHaltingNumber("det_J2_S4")
                
                # Simple AI Logic for Intersection 2 with "coordination"
                # We give extra weight to cars coming from the West (from Intersection 1)
                if ((cars_J2_W * 1.5) + cars_J2_E) > (cars_J2_N + cars_J2_S):
                    if traci.trafficlight.getPhase(TLS_ID_J2) != 0:
                        traci.trafficlight.setPhase(TLS_ID_J2, 0)
                        # Track phase change
                        if prev_j2_phase != 0:
                            metrics.intersection_stats['J2']['phase_changes'] += 1
                        prev_j2_phase = 0
                else:
                    if traci.trafficlight.getPhase(TLS_ID_J2) != 2:
                        traci.trafficlight.setPhase(TLS_ID_J2, 2)
                        # Track phase change
                        if prev_j2_phase != 2:
                            metrics.intersection_stats['J2']['phase_changes'] += 1
                        prev_j2_phase = 2

                # Update intersection vehicle counts
                metrics.intersection_stats['J1']['total_vehicles'] += cars_J1_E + cars_J1_W + cars_J1_N + cars_J1_S
                metrics.intersection_stats['J2']['total_vehicles'] += cars_J2_E + cars_J2_W + cars_J2_N + cars_J2_S

            except traci.TraCIException as e:
                print(f"TraCI error at step {step}: {e}")
                continue  # Continue simulation even if detector reading fails

            # Check for completed vehicle journeys
            try:
                departed_vehicles = traci.simulation.getDepartedIDList()
                arrived_vehicles = traci.simulation.getArrivedIDList()
                
                for veh_id in arrived_vehicles:
                    metrics.log_vehicle_completion(veh_id, step)
                    
            except Exception as e:
                pass  # Ignore vehicle tracking errors

    except KeyboardInterrupt:
        print("Simulation interrupted by user")
    except Exception as e:
        print(f"Simulation error: {e}")
    finally:
        # After the simulation ends, close the connection safely
        try:
            traci.close(wait=False)  # Don't wait for process to close
            print("SUMO simulation closed successfully!")
        except:
            print("Error closing SUMO, but continuing...")
        
        # Finalize metrics collection
        metrics.finalize_metrics()
    
    sys.stdout.flush()

# --- Standard entry point for a Python script ---
if __name__ == "__main__":
    run_simulation()