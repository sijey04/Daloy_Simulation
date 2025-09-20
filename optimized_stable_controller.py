#!/usr/bin/env python3
"""
Optimized Traffic Controller with Fixed SUMO Configuration
Uses the stable configuration created by fix_sumo_issues.py
"""

import os
import sys
import math
import traci
import time
import csv
from datetime import datetime, timedelta

class OptimizedTrafficController:
    def __init__(self):
        self.sumo_binary = None
        self.network_file = "KCCIntersection.net.xml"
        self.route_file = "KCCIntersection_super_visible.rou.xml"
        self.config_file = "KCCIntersection_optimized_stable.sumocfg"
        
        # Traffic light IDs
        self.traffic_lights = ["1017322684", "1017322720"]  # J1 and J2
        
        # Camera system - 360 degree rotation
        self.camera_angles = {"1017322684": 0.0, "1017322720": 180.0}  # Start opposite
        self.camera_rotation_speed = 10.0  # degrees per step
        
        # Enhanced detector mappings for J1 (primary complex intersection)
        self.J1_detectors = {
            'E': ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4', 'det_J1_E5', 'det_J1_E6', 'det_J1_E7', 'det_J1_E8', 'det_J1_E9', 'det_J1_E10'],
            'W': ['det_J1_W1', 'det_J1_W2'],
            'N': ['det_J1_N1', 'det_J1_N2', 'det_J1_N3', 'det_J1_N4'],
            'S': ['det_J1_S1', 'det_J1_S2', 'det_J1_S3', 'det_J1_S4']
        }
        
        # Enhanced detector mappings for J2 (4-way intersection)
        self.J2_detectors = {
            'E': ['det_J2_E1', 'det_J2_E2'],
            'W': ['det_J2_W1', 'det_J2_W2', 'det_J2_W3', 'det_J2_W4'],
            'N': ['det_J2_N1', 'det_J2_N2'],
            'S': ['det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4']
        }
        
        # Traffic metrics storage
        self.metrics = []
        self.last_phase_change = {"1017322684": 0, "1017322720": 0}
        self.phase_change_count = {"1017322684": 0, "1017322720": 0}
        
        print("🚀 OPTIMIZED TRAFFIC CONTROLLER - STABLE CONFIGURATION")
        print("=" * 70)
        print("✅ Using fixed detector configuration")
        print("✅ Enhanced collision handling enabled")
        print("✅ Improved traffic light timing")
        print("✅ Optimized vehicle parameters")
        print("=" * 70)

    def find_sumo_binary(self):
        """Find SUMO binary in PATH"""
        try:
            if 'SUMO_HOME' in os.environ:
                sumo_binary = os.path.join(os.environ['SUMO_HOME'], 'bin', 'sumo-gui.exe')
                if os.path.exists(sumo_binary):
                    self.sumo_binary = sumo_binary
                    return True
            
            # Fallback to PATH
            import subprocess
            result = subprocess.run(['where', 'sumo-gui'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.sumo_binary = result.stdout.strip().split('\n')[0]
                return True
                
        except Exception as e:
            print(f"❌ Error finding SUMO: {e}")
        
        print("❌ SUMO not found. Please install SUMO and set SUMO_HOME environment variable.")
        return False

    def get_camera_focus_direction(self, tl_id):
        """Get camera focus direction based on 360° rotation"""
        angle = self.camera_angles[tl_id] % 360
        
        # Quadrant-based focus with smooth transitions
        if 315 <= angle < 45:  # North quadrant
            primary, secondary = 'N', 'E' if angle < 360 else 'W'
        elif 45 <= angle < 135:  # East quadrant
            primary, secondary = 'E', 'S' if angle < 90 else 'N'
        elif 135 <= angle < 225:  # South quadrant
            primary, secondary = 'S', 'W' if angle < 180 else 'E'
        else:  # West quadrant (225-315)
            primary, secondary = 'W', 'N' if angle < 270 else 'S'
        
        quadrant = ['North', 'East', 'South', 'West'][int((angle + 45) // 90) % 4]
        return primary, secondary, quadrant

    def get_enhanced_traffic_density(self, tl_id):
        """Enhanced traffic density calculation with 360° camera awareness"""
        try:
            # Get camera focus directions
            primary_dir, secondary_dir, quadrant = self.get_camera_focus_direction(tl_id)
            
            # Get detector mappings based on intersection
            if tl_id == "1017322684":  # J1
                detectors = self.J1_detectors
            else:  # J2
                detectors = self.J2_detectors
            
            # Calculate directional densities with camera bias
            densities = {}
            total_vehicles = 0
            
            for direction in ['E', 'W', 'N', 'S']:
                direction_vehicles = 0
                detector_count = 0
                
                if direction in detectors:
                    for det_id in detectors[direction]:
                        try:
                            vehicles = traci.lanearea.getLastStepVehicleNumber(det_id)
                            direction_vehicles += vehicles
                            detector_count += 1
                        except Exception:
                            # Detector might not exist or be unavailable
                            continue
                
                # Camera focus weighting
                if direction == primary_dir:
                    weight = 1.5  # Higher weight for primary focus
                elif direction == secondary_dir:
                    weight = 1.2  # Medium weight for secondary focus
                else:
                    weight = 1.0  # Normal weight
                
                densities[direction] = direction_vehicles * weight
                total_vehicles += direction_vehicles
            
            return densities, total_vehicles
            
        except Exception as e:
            print(f"⚠️ Traffic density calculation error for {tl_id}: {e}")
            return {'E': 0, 'W': 0, 'N': 0, 'S': 0}, 0

    def calculate_urgency_score(self, densities):
        """Calculate traffic urgency with enhanced weighting"""
        try:
            ew_traffic = densities['E'] + densities['W']
            ns_traffic = densities['N'] + densities['S']
            
            # Enhanced urgency calculation
            if ew_traffic > 0 and ns_traffic > 0:
                # Both directions have traffic - calculate ratio
                ratio = max(ew_traffic, ns_traffic) / min(ew_traffic, ns_traffic)
                urgency_ew = ew_traffic * (1 + math.log(ratio + 1))
                urgency_ns = ns_traffic * (1 + math.log(ratio + 1))
            else:
                urgency_ew = ew_traffic * 2  # Boost when only one direction
                urgency_ns = ns_traffic * 2
            
            return urgency_ew, urgency_ns
            
        except Exception as e:
            print(f"⚠️ Urgency calculation error: {e}")
            return 0, 0

    def should_change_phase(self, tl_id, densities, current_step):
        """Enhanced phase change logic with minimum green time"""
        try:
            current_phase = traci.trafficlight.getPhase(tl_id)
            time_since_change = current_step - self.last_phase_change[tl_id]
            
            # Minimum green time (30 seconds = 30 steps)
            min_green_time = 30
            if time_since_change < min_green_time:
                return False, current_phase
            
            urgency_ew, urgency_ns = self.calculate_urgency_score(densities)
            
            # Enhanced phase logic with improved thresholds
            if current_phase == 0:  # EW Green
                # Switch to NS if NS has significantly higher urgency
                if urgency_ns > urgency_ew * 1.3 and urgency_ns > 3:
                    return True, 2  # Switch to NS Green
            elif current_phase == 2:  # NS Green
                # Switch to EW if EW has significantly higher urgency
                if urgency_ew > urgency_ns * 1.3 and urgency_ew > 3:
                    return True, 0  # Switch to EW Green
            
            return False, current_phase
            
        except Exception as e:
            print(f"⚠️ Phase change logic error for {tl_id}: {e}")
            return False, 0

    def update_camera_angles(self):
        """Update 360° rotating camera angles"""
        for tl_id in self.camera_angles:
            self.camera_angles[tl_id] = (self.camera_angles[tl_id] + self.camera_rotation_speed) % 360

    def control_traffic_lights(self, current_step):
        """Enhanced traffic light control with 360° camera system"""
        try:
            # Update camera positions
            self.update_camera_angles()
            
            for tl_id in self.traffic_lights:
                # Get enhanced traffic data
                densities, total_vehicles = self.get_enhanced_traffic_density(tl_id)
                
                # Check for phase change
                should_change, new_phase = self.should_change_phase(tl_id, densities, current_step)
                
                if should_change:
                    traci.trafficlight.setPhase(tl_id, new_phase)
                    self.last_phase_change[tl_id] = current_step
                    self.phase_change_count[tl_id] += 1
                    
                    urgency_ew, urgency_ns = self.calculate_urgency_score(densities)
                    direction = "EW" if new_phase == 0 else "NS"
                    tl_name = "J1" if tl_id == "1017322684" else "J2"
                    
                    print(f"{tl_name} Phase Change at step {current_step}: → Phase {new_phase} "
                          f"({direction}: {urgency_ew:.1f}, NS: {urgency_ns:.1f})")
                
                # Display camera status every 10 steps
                if current_step % 20 == 0:
                    primary, secondary, quadrant = self.get_camera_focus_direction(tl_id)
                    tl_name = "J1" if tl_id == "1017322684" else "J2"
                    angle = self.camera_angles[tl_id]
                    print(f"🎥 {tl_name} Camera: {angle:.1f}° - {quadrant} Quadrant | "
                          f"Focus: {primary}(Primary), {secondary}(Secondary)")
            
        except Exception as e:
            print(f"⚠️ Traffic control error: {e}")

    def collect_metrics(self, current_step):
        """Collect comprehensive traffic metrics"""
        try:
            # Get overall network stats
            vehicles_in_network = traci.simulation.getMinExpectedNumber()
            
            # Calculate queue lengths for each intersection
            j1_queue = sum(self.get_enhanced_traffic_density("1017322684")[1] for _ in [1])
            j2_queue = sum(self.get_enhanced_traffic_density("1017322720")[1] for _ in [1])
            
            # Store metrics
            hour = current_step // 3600
            metrics_data = {
                'step': current_step,
                'hour': hour,
                'vehicles': vehicles_in_network,
                'j1_queue': j1_queue,
                'j2_queue': j2_queue,
                'j1_camera_angle': self.camera_angles["1017322684"],
                'j2_camera_angle': self.camera_angles["1017322720"]
            }
            
            self.metrics.append(metrics_data)
            
            # Hourly progress report
            if current_step % 3600 == 0 and current_step > 0:
                print(f"Hour {hour:3d} | Step {current_step:8d} | Vehicles: {vehicles_in_network:3d} | "
                      f"J1 Queue: {j1_queue:2d} | J2 Queue: {j2_queue:2d}")
                print(f"        🎥 J1 Camera: {self.camera_angles['1017322684']:.1f}° "
                      f"({self.get_camera_focus_direction('1017322684')[2]} Quadrant) | "
                      f"J2 Camera: {self.camera_angles['1017322720']:.1f}° "
                      f"({self.get_camera_focus_direction('1017322720')[2]} Quadrant)")
            
        except Exception as e:
            print(f"⚠️ Metrics collection error: {e}")

    def save_metrics(self, filename="stable_traffic_metrics.csv"):
        """Save collected metrics to CSV"""
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['step', 'hour', 'vehicles', 'j1_queue', 'j2_queue', 'j1_camera_angle', 'j2_camera_angle']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.metrics)
            print(f"✅ Metrics saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving metrics: {e}")

    def run_simulation(self, duration_hours=24):
        """Run optimized traffic simulation with stable configuration"""
        if not self.find_sumo_binary():
            return False
        
        duration_steps = duration_hours * 3600
        print(f"\n🚀 STARTING STABLE SUMO SIMULATION")
        print(f"📊 Duration: {duration_hours} hours ({duration_steps:,} steps)")
        print(f"⚙️ Configuration: {self.config_file}")
        print("=" * 70)
        
        try:
            # Start SUMO with stable configuration
            sumo_cmd = [
                self.sumo_binary,
                "-c", self.config_file,
                "--start", "true",
                "--quit-on-end", "false"
            ]
            
            traci.start(sumo_cmd)
            print("✅ Connected to SUMO-GUI with stable configuration")
            print("✅ Enhanced collision handling enabled")
            print("✅ Fixed detector configuration loaded")
            print("✅ Starting optimized traffic control...")
            
            start_time = time.time()
            
            # Main simulation loop
            for step in range(duration_steps):
                traci.simulationStep()
                
                # Control traffic lights with 360° camera system
                self.control_traffic_lights(step)
                
                # Collect metrics
                self.collect_metrics(step)
                
                # Safety check - stop if no more vehicles and past initial phase
                if step > 1800 and traci.simulation.getMinExpectedNumber() == 0:
                    print(f"\n⚠️ Simulation ended early at step {step} - no more vehicles")
                    break
            
            traci.close()
            
            elapsed_time = time.time() - start_time
            print(f"\n✅ STABLE SIMULATION COMPLETE!")
            print("=" * 50)
            print(f"Performance Summary:")
            print(f"   • J1 Phase changes: {self.phase_change_count['1017322684']}")
            print(f"   • J2 Phase changes: {self.phase_change_count['1017322720']}")
            print(f"   • Simulation duration: {step + 1} steps")
            
            # Save metrics
            self.save_metrics()
            print(f"[SUCCESS] Stable simulation completed in {elapsed_time/60:.1f} minutes")
            return True
            
        except Exception as e:
            print(f"\n❌ Simulation error: {e}")
            try:
                traci.close()
            except:
                pass
            return False

def main():
    print("🎯 OPTIMIZED TRAFFIC CONTROLLER - STABLE VERSION")
    print("=" * 70)
    print("Features:")
    print("• Fixed detector configuration (no warnings)")
    print("• Enhanced collision handling") 
    print("• Improved traffic light timing")
    print("• 360° rotating camera system")
    print("• Optimized vehicle parameters")
    print("=" * 70)
    
    controller = OptimizedTrafficController()
    
    # Run 24-hour stable simulation
    success = controller.run_simulation(duration_hours=24)
    
    if success:
        print("\n🎉 SIMULATION COMPLETED SUCCESSFULLY!")
        print("📊 Metrics saved to: stable_traffic_metrics.csv")
        print("✅ No SUMO warnings expected with fixed configuration")
    else:
        print("\n❌ Simulation failed")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()