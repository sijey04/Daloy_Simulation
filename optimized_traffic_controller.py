# =============================================================================
#           OPTIMIZED SMART TRAFFIC CONTROL SYSTEM - ZAMBOANGA KCC
#           WITH REALISTIC TRAFFIC PARAMETERS & ENHANCED COORDINATION
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

# --- Optimized AI Traffic Controller Class ---
class OptimizedTrafficController:
    def __init__(self):
        # OPTIMIZED PARAMETERS FOR REALISTIC TRAFFIC - FASTER CAMERA ROTATION
        self.camera_rotation_speed = 10  # Increased: 10° per step for faster rotation
        self.prediction_window = 15      # Longer prediction window
        
        # 360° ROTATING CAMERA PARAMETERS - NORMAL ROTATION
        self.j1_camera_angle = 0        # Current J1 camera angle (0-360°)
        self.j2_camera_angle = 180      # Current J2 camera angle (start opposite)
        self.field_of_view = 90         # Camera field of view in degrees
        
        # IMPROVED TIMING PARAMETERS - SAME RESPONSE AS BASELINE
        self.min_green_time = 20        # Restored: 20s minimum green time
        self.max_green_time = 90        # Restored: 90s maximum green time
        self.yellow_time = 3
        
        # Phase timing tracking
        self.j1_phase_timer = 0
        self.j2_phase_timer = 0
        self.j1_last_change = 0
        self.j2_last_change = 0
        
        # Traffic pattern analysis
        self.traffic_history = {
            'J1': {'E': [], 'W': [], 'N': [], 'S': []},
            'J2': {'E': [], 'W': [], 'N': [], 'S': []}
        }
        
        # OPTIMIZED PARAMETERS
        self.congestion_threshold = 18  # INCREASED: 8 → 18 vehicles
        self.emergency_threshold = 25   # NEW: Emergency mode threshold
        self.coordination_weight = 2.5  # INCREASED coordination
        self.queue_clearing_bonus = 3.0 # NEW: Bonus for clearing queues
        
    def get_360_camera_data(self, intersection, step):
        """TRUE 360° ROTATING CAMERA SYSTEM - Like Your Diagrams!"""
        
        # Update camera rotation angle
        if intersection == 'J1':
            self.j1_camera_angle = (self.j1_camera_angle + self.camera_rotation_speed) % 360
            camera_angle = self.j1_camera_angle
        else:  # J2
            self.j2_camera_angle = (self.j2_camera_angle + self.camera_rotation_speed) % 360
            camera_angle = self.j2_camera_angle
        
        # Determine camera focus areas (like your diagrams)
        primary_direction, secondary_direction = self.get_camera_focus(camera_angle)
        
        # Print rotation status for visibility - FASTER CAMERA UPDATES  
        if step % 36 == 0:  # Every 36 steps (faster updates for 10° rotation)
            quadrant = self.get_quadrant_name(camera_angle)
            print(f"🎥 {intersection} Camera: {camera_angle:.1f}° - {quadrant} | Focus: {primary_direction}(Primary), {secondary_direction}(Secondary)")
        
        try:
            if intersection == 'J1':
                # Complete detector coverage for J1 with 4-lane east approach
                detectors = {
                    'E': ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4', 
                          'det_J1_E5', 'det_J1_E6', 'det_J1_E7', 'det_J1_E8', 
                          'det_J1_E9', 'det_J1_E10'],
                    'W': ['det_J1_W1', 'det_J1_W2'],
                    'N': ['det_J1_N1', 'det_J1_N2', 'det_J1_N3', 'det_J1_N4'],
                    'S': ['det_J1_S1', 'det_J1_S2', 'det_J1_S3', 'det_J1_S4']
                }
            else:  # J2
                detectors = {
                    'E': ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4', 'det_J2_E5', 'det_J2_E6'],
                    'W': ['det_J2_W1', 'det_J2_W2', 'det_J2_W3', 'det_J2_W4'],
                    'N': ['det_J2_N1', 'det_J2_N2'],
                    'S': ['det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4']
                }
            
            # ROTATING CAMERA DATA COLLECTION WITH VISIBILITY FACTORS
            traffic_data = {}
            
            for direction in ['E', 'W', 'N', 'S']:
                # Calculate visibility factor based on camera rotation
                visibility_factor = self.calculate_camera_visibility(direction, primary_direction, secondary_direction)
                
                try:
                    # Get raw detector data
                    raw_halting = sum(traci.lanearea.getLastStepHaltingNumber(det) for det in detectors[direction])
                    raw_total = sum(traci.lanearea.getLastStepVehicleNumber(det) for det in detectors[direction])
                    raw_waiting = self.calculate_direction_waiting_time(detectors[direction])
                    
                    # Apply camera visibility factor (realistic rotation effect)
                    traffic_data[f'{direction}_halting'] = int(raw_halting * visibility_factor)
                    traffic_data[f'{direction}_total'] = int(raw_total * visibility_factor)
                    traffic_data[f'{direction}_waiting'] = raw_waiting * visibility_factor
                    
                except Exception as e:
                    # Camera can't see this direction clearly
                    traffic_data[f'{direction}_halting'] = 0
                    traffic_data[f'{direction}_total'] = 0
                    traffic_data[f'{direction}_waiting'] = 0
            
            # Store in history for trend analysis (use primary direction data for most accurate trends)
            primary_data = traffic_data[f'{primary_direction}_halting']
            self.traffic_history[intersection][primary_direction].append(primary_data)
            
            # Keep recent history
            for direction in ['E', 'W', 'N', 'S']:
                if len(self.traffic_history[intersection][direction]) > 10:
                    self.traffic_history[intersection][direction].pop(0)
            
            return traffic_data
            
        except Exception as e:
            print(f"360° Rotating Camera error at {intersection}: {e}")
            return {
                'E_halting': 0, 'W_halting': 0, 'N_halting': 0, 'S_halting': 0,
                'E_total': 0, 'W_total': 0, 'N_total': 0, 'S_total': 0,
                'E_waiting': 0, 'W_waiting': 0, 'N_waiting': 0, 'S_waiting': 0
            }
    
    def get_camera_focus(self, angle):
        """Determine camera focus based on rotation angle (like your diagrams)"""
        angle = angle % 360
        
        # Define focus quadrants matching your diagram patterns
        if 315 <= angle or angle < 45:      # 0° ± 45° = East focus (Green area)
            return 'E', 'N' if angle < 22.5 or angle > 337.5 else 'S'
        elif 45 <= angle < 135:             # 90° ± 45° = North focus (Green area)
            return 'N', 'E' if angle < 90 else 'W'
        elif 135 <= angle < 225:            # 180° ± 45° = West focus (Green area)
            return 'W', 'N' if angle < 180 else 'S'
        elif 225 <= angle < 315:            # 270° ± 45° = South focus (Green area)
            return 'S', 'W' if angle < 270 else 'E'
        
        return 'E', 'N'  # Default
    
    def calculate_camera_visibility(self, direction, primary, secondary):
        """Calculate visibility factor based on camera focus (like your diagrams)"""
        if direction == primary:
            return 1.0      # Full visibility - Green area in your diagram
        elif direction == secondary:
            return 0.75     # Good visibility - Blue area in your diagram
        else:
            return 0.25     # Limited visibility - Outside focus areas
    
    def get_quadrant_name(self, angle):
        """Get readable quadrant name for the angle"""
        angle = angle % 360
        if 315 <= angle or angle < 45:
            return "East Quadrant"
        elif 45 <= angle < 135:
            return "North Quadrant"
        elif 135 <= angle < 225:
            return "West Quadrant"
        elif 225 <= angle < 315:
            return "South Quadrant"
        return "East Quadrant"
    
    def calculate_direction_waiting_time(self, detectors):
        """Calculate average waiting time for a specific direction"""
        try:
            total_waiting = 0
            vehicle_count = 0
            for det in detectors:
                try:
                    vehicles = traci.lanearea.getLastStepVehicleIDs(det)
                    for veh_id in vehicles:
                        waiting_time = traci.vehicle.getWaitingTime(veh_id)
                        total_waiting += waiting_time
                        vehicle_count += 1
                except:
                    continue
            return total_waiting / max(1, vehicle_count)
        except:
            return 0
    
    def calculate_urgency_score(self, traffic_data, intersection, direction_pair):
        """OPTIMIZED urgency calculation for realistic traffic"""
        if direction_pair == 'EW':
            halting = traffic_data['E_halting'] + traffic_data['W_halting']
            total = traffic_data['E_total'] + traffic_data['W_total']
            waiting = (traffic_data['E_waiting'] + traffic_data['W_waiting']) / 2
            trend_e = self.predict_traffic_trend(intersection, 'E')
            trend_w = self.predict_traffic_trend(intersection, 'W')
            trend = max(trend_e, trend_w)
        else:  # NS
            halting = traffic_data['N_halting'] + traffic_data['S_halting']
            total = traffic_data['N_total'] + traffic_data['S_total']
            waiting = (traffic_data['N_waiting'] + traffic_data['S_waiting']) / 2
            trend_n = self.predict_traffic_trend(intersection, 'N')
            trend_s = self.predict_traffic_trend(intersection, 'S')
            trend = max(trend_n, trend_s)
        
        # OPTIMIZED urgency calculation
        urgency_score = (
            halting * 4.0 +                    # Increased weight for halting vehicles
            total * 1.5 +                      # Increased weight for total vehicles
            waiting * 0.8 +                    # Increased weight for waiting time
            max(0, trend) * 2.5                # Increased trend weight
        )
        
        # ENHANCED emergency handling
        if halting >= self.emergency_threshold:
            urgency_score *= 2.0               # Emergency multiplier
            print(f"EMERGENCY: {intersection} severe congestion detected ({halting} vehicles halting)")
        elif halting >= self.congestion_threshold:
            urgency_score *= 1.5               # Congestion multiplier
        
        # Queue clearing bonus
        if halting > 0:
            urgency_score += self.queue_clearing_bonus * halting
        
        return urgency_score
    
    def predict_traffic_trend(self, intersection, direction):
        """Enhanced traffic trend prediction"""
        history = self.traffic_history[intersection][direction]
        if len(history) < 5:
            return 0
        
        # Enhanced trend analysis
        recent = history[-5:]
        if len(recent) >= 3:
            trend = (recent[-1] - recent[0]) / len(recent)
            return trend
        return 0
    
    def optimized_traffic_control(self, step, tls_j1_id, tls_j2_id, metrics):
        """OPTIMIZED traffic control logic with ROTATING CAMERAS"""
        
        # ROTATING CAMERA data collection every step for smooth rotation
        j1_data = self.get_360_camera_data('J1', step)
        j2_data = self.get_360_camera_data('J2', step)
        
        # Update phase timers every step
        self.j1_phase_timer += 1
        self.j2_phase_timer += 1
        
        # OPTIMIZED LOGIC FOR INTERSECTION 1 (J1)
        current_j1_phase = traci.trafficlight.getPhase(tls_j1_id)
        
        # Calculate urgency scores
        j1_ew_urgency = self.calculate_urgency_score(j1_data, 'J1', 'EW')
        j1_ns_urgency = self.calculate_urgency_score(j1_data, 'J1', 'NS')
        
        # ENHANCED decision logic with LONGER minimum times
        phase_change_needed = False
        target_j1_phase = current_j1_phase
        
        if current_j1_phase == 0:  # Currently EW green
            # REQUIRE LONGER minimum time before switching
            if (j1_ns_urgency > j1_ew_urgency * 1.5 and 
                self.j1_phase_timer >= self.min_green_time):
                target_j1_phase = 2  # Switch to NS green
                phase_change_needed = True
            elif self.j1_phase_timer >= self.max_green_time:
                target_j1_phase = 2  # Force switch after max time
                phase_change_needed = True
        
        elif current_j1_phase == 2:  # Currently NS green
            if (j1_ew_urgency > j1_ns_urgency * 1.5 and 
                self.j1_phase_timer >= self.min_green_time):
                target_j1_phase = 0  # Switch to EW green
                phase_change_needed = True
            elif self.j1_phase_timer >= self.max_green_time:
                target_j1_phase = 0  # Force switch after max time
                phase_change_needed = True
        
        # Execute J1 phase change
        if phase_change_needed:
            traci.trafficlight.setPhase(tls_j1_id, target_j1_phase)
            self.j1_phase_timer = 0
            self.j1_last_change = step
            metrics.intersection_stats['J1']['phase_changes'] += 1
            print(f"J1 Phase Change at step {step}: → Phase {target_j1_phase} (EW: {j1_ew_urgency:.1f}, NS: {j1_ns_urgency:.1f})")
        
        # OPTIMIZED LOGIC FOR INTERSECTION 2 (J2)
        if tls_j2_id is not None:  # Only control J2 if it has traffic lights
            current_j2_phase = traci.trafficlight.getPhase(tls_j2_id)
            
            # Calculate urgency scores with enhanced coordination
            j2_ew_urgency = self.calculate_urgency_score(j2_data, 'J2', 'EW')
            j2_ns_urgency = self.calculate_urgency_score(j2_data, 'J2', 'NS')
            
            # ENHANCED coordination with J1
            if target_j1_phase == 0:  # J1 is EW green
                j2_ew_urgency *= self.coordination_weight
            
            # Consider J1's recent changes
            steps_since_j1_change = step - self.j1_last_change
            if steps_since_j1_change < 40:  # Longer coordination window
                if target_j1_phase == 0:
                    j2_ew_urgency *= 1.3  # Boost J2 EW when J1 is EW
            
            # ENHANCED decision logic for J2
            phase_change_needed_j2 = False
            target_j2_phase = current_j2_phase
            
            if current_j2_phase == 0:  # Currently EW green
                if (j2_ns_urgency > j2_ew_urgency * 1.4 and 
                    self.j2_phase_timer >= self.min_green_time):
                    target_j2_phase = 2  # Switch to NS green
                    phase_change_needed_j2 = True
                elif self.j2_phase_timer >= self.max_green_time:
                    target_j2_phase = 2  # Force switch after max time
                    phase_change_needed_j2 = True
            
            elif current_j2_phase == 2:  # Currently NS green
                if (j2_ew_urgency > j2_ns_urgency * 1.4 and 
                    self.j2_phase_timer >= self.min_green_time):
                    target_j2_phase = 0  # Switch to EW green
                    phase_change_needed_j2 = True
                elif self.j2_phase_timer >= self.max_green_time:
                    target_j2_phase = 0  # Force switch after max time
                    phase_change_needed_j2 = True
            
            # Execute J2 phase change
            if phase_change_needed_j2:
                traci.trafficlight.setPhase(tls_j2_id, target_j2_phase)
                self.j2_phase_timer = 0
                self.j2_last_change = step
                metrics.intersection_stats['J2']['phase_changes'] += 1
                print(f"J2 Phase Change at step {step}: → Phase {target_j2_phase} (EW: {j2_ew_urgency:.1f}, NS: {j2_ns_urgency:.1f})")
        else:
            # J2 has no traffic lights - it operates as a 4-way stop or uncontrolled
            # Still collect data for comparison purposes
            pass
        
        # Update metrics
        metrics.intersection_stats['J1']['total_vehicles'] += (
            j1_data['E_total'] + j1_data['W_total'] + j1_data['N_total'] + j1_data['S_total']
        )
        metrics.intersection_stats['J2']['total_vehicles'] += (
            j2_data['E_total'] + j2_data['W_total'] + j2_data['N_total'] + j2_data['S_total']
        )

# --- Metrics Collection Class ---
class TrafficMetrics:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_data = []
        self.vehicle_data = {}
        self.intersection_stats = {
            'J1': {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0},
            'J2': {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0}
        }
        self.init_csv_files()
    
    def init_csv_files(self):
        """Initialize CSV files for metrics logging"""
        with open('traffic_metrics_500h.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Step', 'Time', 'Vehicles', 'J1_Phase', 'J2_Phase', 
                           'J1_Queue', 'J2_Queue', 'J1_Waiting', 'J2_Waiting'])
    
    def collect_step_metrics(self, step, tls_j1_id, tls_j2_id):
        """Collect optimized metrics"""
        try:
            current_time = step
            total_vehicles = traci.simulation.getMinExpectedNumber()
            j1_phase = traci.trafficlight.getPhase(tls_j1_id)
            j2_phase = traci.trafficlight.getPhase(tls_j2_id) if tls_j2_id is not None else -1
            
            # Calculate queue lengths
            j1_queue = self.calculate_queue_length('J1')
            j2_queue = self.calculate_queue_length('J2')
            
            # Calculate waiting times  
            j1_waiting = self.calculate_intersection_waiting_time('J1')
            j2_waiting = self.calculate_intersection_waiting_time('J2')
            
            # Save to CSV
            with open('optimized_traffic_metrics.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([step, current_time, total_vehicles, j1_phase, j2_phase,
                               j1_queue, j2_queue, j1_waiting, j2_waiting])
            
        except Exception as e:
            print(f"Metrics collection error: {e}")
    
    def calculate_queue_length(self, intersection):
        """Calculate queue length using enhanced detector coverage"""
        try:
            if intersection == 'J1':
                detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4',
                           'det_J1_E5', 'det_J1_E6', 'det_J1_E7', 'det_J1_E8',
                           'det_J1_E9', 'det_J1_E10',
                           'det_J1_W1', 'det_J1_W2', 'det_J1_N1', 'det_J1_N2',
                           'det_J1_N3', 'det_J1_N4', 'det_J1_S1', 'det_J1_S2',
                           'det_J1_S3', 'det_J1_S4']
            else:  # J2
                detectors = ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4',
                           'det_J2_E5', 'det_J2_E6', 'det_J2_W1', 'det_J2_W2',
                           'det_J2_W3', 'det_J2_W4', 'det_J2_N1', 'det_J2_N2',
                           'det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4']
            
            total_halting = sum(traci.lanearea.getLastStepHaltingNumber(det) for det in detectors)
            return total_halting
            
        except:
            return 0
    
    def calculate_intersection_waiting_time(self, intersection):
        """Calculate average waiting time for intersection"""
        try:
            if intersection == 'J1':
                detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4',
                           'det_J1_E5', 'det_J1_E6', 'det_J1_E7', 'det_J1_E8',
                           'det_J1_E9', 'det_J1_E10',
                           'det_J1_W1', 'det_J1_W2', 'det_J1_N1', 'det_J1_N2',
                           'det_J1_N3', 'det_J1_N4', 'det_J1_S1', 'det_J1_S2',
                           'det_J1_S3', 'det_J1_S4']
            else:
                detectors = ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4',
                           'det_J2_E5', 'det_J2_E6', 'det_J2_W1', 'det_J2_W2',
                           'det_J2_W3', 'det_J2_W4', 'det_J2_N1', 'det_J2_N2',
                           'det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4']
            
            total_waiting = 0
            vehicle_count = 0
            for det in detectors:
                try:
                    vehicles = traci.lanearea.getLastStepVehicleIDs(det)
                    for veh_id in vehicles:
                        waiting_time = traci.vehicle.getWaitingTime(veh_id)
                        total_waiting += waiting_time
                        vehicle_count += 1
                except:
                    continue
            
            return total_waiting / max(1, vehicle_count)
        except:
            return 0

# --- Main Optimized Simulation Function ---
def run_optimized_simulation():
    """Run the optimized simulation with realistic traffic"""
    
    print("OPTIMIZED SUMO SIMULATION - 500 HOUR REALISTIC TRAFFIC - FASTER CAMERAS")
    print("=" * 70)
    print("Features: TRUE 360° ROTATING CAMERAS + Optimized Controller")
    print("Simulation Duration: 24 HOURS (86,400 steps)")
    print("SIMULATION SPEED: NORMAL (Same as Baseline)")
    print("   • Simulation Delay: Default (~100ms)")
    print("   • Camera Rotation: 10°/step (faster rotation)")
    print("   • Normal Traffic Light Timing")
    print("🎥 ROTATING CAMERA SYSTEM:")
    print("   • J1 Camera: Starts at 0° (East focus)")
    print("   • J2 Camera: Starts at 180° (West focus)")
    print("   • Rotation Speed: 10° per step (faster rotation)")
    print("   • Field of View: 90° with focus areas")
    print("Enhanced Parameters:")
    print("   • Min Green Time: 20 seconds (normal timing)")
    print("   • Max Green Time: 90 seconds (normal cycles)")
    print("   • Congestion Threshold: 18 vehicles")
    print("   • Emergency Threshold: 25 vehicles")
    print("   • Enhanced Coordination & Queue Clearing")
    print("=" * 70)
    
    # Initialize optimized controller and metrics
    controller = OptimizedTrafficController()
    metrics = TrafficMetrics()
    
    # Start SUMO with GUI for visual rotation monitoring - SAME SPEED AS BASELINE
    try:
        traci.start(["sumo-gui", "-c", "KCCIntersection_optimized.sumocfg",
                    "--start", "--quit-on-end"])
    except Exception as e:
        print(f"SUMO startup error: {e}")
        return

    # Traffic Light IDs
    TLS_ID_J1 = "1017322684"
    TLS_ID_J2 = "1017322720"
    
    # Check if traffic lights exist
    available_tls = traci.trafficlight.getIDList()
    print(f"Available traffic lights: {available_tls}")
    
    j1_exists = TLS_ID_J1 in available_tls
    j2_exists = TLS_ID_J2 in available_tls
    
    if not j1_exists:
        print(f"ERROR: J1 traffic light {TLS_ID_J1} not found!")
        traci.close()
        return
    
    if not j2_exists:
        print(f"WARNING: J2 traffic light {TLS_ID_J2} not found! J2 will operate without signals.")
        TLS_ID_J2 = None
    
    # Track phases
    prev_j1_phase = traci.trafficlight.getPhase(TLS_ID_J1)
    prev_j2_phase = traci.trafficlight.getPhase(TLS_ID_J2) if j2_exists else -1

    try:
        print("Starting optimized traffic control simulation...")
        step = 0
        
        while step < 86400:  # 24 hours = 86,400 steps (continue regardless of vehicle count)
            step += 1
            traci.simulationStep()
            
            # Run optimized traffic control
            controller.optimized_traffic_control(step, TLS_ID_J1, TLS_ID_J2, metrics)
            
            # Collect metrics every 10 steps (normal simulation speed)
            if step % 10 == 0:
                metrics.collect_step_metrics(step, TLS_ID_J1, TLS_ID_J2)
            
            # Progress reporting with camera rotation status - NORMAL UPDATES
            if step % 3600 == 0:  # Every hour (normal reporting frequency)
                vehicles = traci.simulation.getMinExpectedNumber()
                j1_phase = traci.trafficlight.getPhase(TLS_ID_J1)
                j2_phase = traci.trafficlight.getPhase(TLS_ID_J2) if TLS_ID_J2 is not None else -1
                j1_queue = metrics.calculate_queue_length('J1')
                j2_queue = metrics.calculate_queue_length('J2')
                hour = step // 3600
                
                # Camera rotation status
                j1_quadrant = controller.get_quadrant_name(controller.j1_camera_angle)
                j2_quadrant = controller.get_quadrant_name(controller.j2_camera_angle)
                
                print(f"Hour {hour:3d} | Step {step:7d} | Vehicles: {vehicles:3d} | J1 Queue: {j1_queue:2d} | J2 Queue: {j2_queue:2d}")
                print(f"        🎥 J1 Camera: {controller.j1_camera_angle:.1f}° ({j1_quadrant}) | J2 Camera: {controller.j2_camera_angle:.1f}° ({j2_quadrant})")

    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    except Exception as e:
        print(f"Simulation error: {e}")
    finally:
        traci.close()
        print("\nOPTIMIZED SIMULATION COMPLETE!")
        print("=" * 50)
        print(f"Performance Summary:")
        print(f"   • J1 Phase changes: {metrics.intersection_stats['J1']['phase_changes']}")
        print(f"   • J2 Phase changes: {metrics.intersection_stats['J2']['phase_changes']}")
        print(f"   • Simulation duration: {step} steps")
        print(f"Results saved to: traffic_metrics_500h.csv")

if __name__ == "__main__":
    run_optimized_simulation()