#!/usr/bin/env python3
"""
Example: True 360° Camera Rotation Implementation
Based on the user's diagrams showing sequential quadrant scanning
"""

import math

class RotatingCameraController:
    def __init__(self):
        self.camera_rotation_speed = 2  # degrees per step
        self.current_angle_j1 = 0       # J1 camera angle
        self.current_angle_j2 = 0       # J2 camera angle
        self.field_of_view = 90         # Camera FOV in degrees
        
    def get_rotating_camera_data(self, intersection, step):
        """Simulate actual 360° rotating camera like the diagrams"""
        
        # Calculate current camera angle
        if intersection == 'J1':
            self.current_angle_j1 = (step * self.camera_rotation_speed) % 360
            camera_angle = self.current_angle_j1
        else:  # J2
            self.current_angle_j2 = (step * self.camera_rotation_speed) % 360
            camera_angle = self.current_angle_j2
        
        # Determine which directions are in camera's field of view
        primary_direction, secondary_direction = self.get_camera_focus(camera_angle)
        
        print(f"{intersection} Camera at {camera_angle:.1f}° - Focus: {primary_direction} (Primary), {secondary_direction} (Secondary)")
        
        # Collect data with rotation-based visibility
        traffic_data = {}
        
        if intersection == 'J1':
            detectors = {
                'E': ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4', 'det_J1_E5'],
                'W': ['det_J1_W1', 'det_J1_W2'],
                'N': ['det_J1_N1', 'det_J1_N2', 'det_J1_N3', 'det_J1_N4'],
                'S': ['det_J1_S1', 'det_J1_S2', 'det_J1_S3', 'det_J1_S4']
            }
        else:  # J2
            detectors = {
                'E': ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4'],
                'W': ['det_J2_W1', 'det_J2_W2', 'det_J2_W3', 'det_J2_W4'],
                'N': ['det_J2_N1', 'det_J2_N2'],
                'S': ['det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4']
            }
        
        # Simulate camera visibility based on rotation
        for direction in ['E', 'W', 'N', 'S']:
            visibility_factor = self.calculate_visibility(direction, primary_direction, secondary_direction)
            
            # Only get data for directions within camera's field of view
            if visibility_factor > 0:
                try:
                    # Simulate reduced accuracy for non-primary directions
                    halting_count = sum(traci.lanearea.getLastStepHaltingNumber(det) for det in detectors[direction])
                    total_count = sum(traci.lanearea.getLastStepVehicleNumber(det) for det in detectors[direction])
                    
                    # Apply visibility factor (primary = 1.0, secondary = 0.7, others = 0.3)
                    traffic_data[f'{direction}_halting'] = int(halting_count * visibility_factor)
                    traffic_data[f'{direction}_total'] = int(total_count * visibility_factor)
                    traffic_data[f'{direction}_waiting'] = self.calculate_direction_waiting_time(detectors[direction]) * visibility_factor
                except:
                    traffic_data[f'{direction}_halting'] = 0
                    traffic_data[f'{direction}_total'] = 0
                    traffic_data[f'{direction}_waiting'] = 0
            else:
                # Camera can't see this direction - no data
                traffic_data[f'{direction}_halting'] = 0
                traffic_data[f'{direction}_total'] = 0
                traffic_data[f'{direction}_waiting'] = 0
        
        return traffic_data, camera_angle
    
    def get_camera_focus(self, angle):
        """Determine camera focus based on rotation angle (like the diagrams)"""
        # Normalize angle to 0-360
        angle = angle % 360
        
        # Define focus quadrants (like your diagrams)
        if 315 <= angle or angle < 45:      # 0° ± 45° = East focus
            return 'E', 'N' if angle < 22.5 or angle > 337.5 else 'S'
        elif 45 <= angle < 135:             # 90° ± 45° = North focus  
            return 'N', 'E' if angle < 90 else 'W'
        elif 135 <= angle < 225:            # 180° ± 45° = West focus
            return 'W', 'N' if angle < 180 else 'S'
        elif 225 <= angle < 315:            # 270° ± 45° = South focus
            return 'S', 'W' if angle < 270 else 'E'
        
        return 'E', 'N'  # Default
    
    def calculate_visibility(self, direction, primary, secondary):
        """Calculate visibility factor based on camera focus"""
        if direction == primary:
            return 1.0      # Full visibility (green area in your diagram)
        elif direction == secondary:
            return 0.7      # Partial visibility (blue area in your diagram)
        else:
            return 0.3      # Limited visibility (peripheral)
    
    def get_rotation_status(self, intersection):
        """Get current rotation status for display"""
        if intersection == 'J1':
            angle = self.current_angle_j1
        else:
            angle = self.current_angle_j2
            
        primary, secondary = self.get_camera_focus(angle)
        
        return {
            'angle': angle,
            'primary_focus': primary,
            'secondary_focus': secondary,
            'quadrant': self.get_quadrant_name(angle)
        }
    
    def get_quadrant_name(self, angle):
        """Get quadrant name for the angle"""
        if 315 <= angle or angle < 45:
            return "East Quadrant"
        elif 45 <= angle < 135:
            return "North Quadrant"
        elif 135 <= angle < 225:
            return "West Quadrant"
        elif 225 <= angle < 315:
            return "South Quadrant"

# Example usage showing the difference:
def demonstrate_rotation():
    """Show how true rotation differs from static coverage"""
    
    print("🎥 TRUE ROTATING CAMERA (Like Your Diagrams)")
    print("=" * 50)
    
    rotating_camera = RotatingCameraController()
    
    # Simulate 4 time steps (180° rotation)
    for step in range(0, 180, 45):
        print(f"\nStep {step}: ")
        
        # J1 Camera rotation
        j1_data, j1_angle = rotating_camera.get_rotating_camera_data('J1', step)
        j1_status = rotating_camera.get_rotation_status('J1')
        
        print(f"  J1 Camera: {j1_angle:.1f}° - {j1_status['quadrant']}")
        print(f"  Primary Focus: {j1_status['primary_focus']}, Secondary: {j1_status['secondary_focus']}")
        
        # Show which directions have data
        visible_directions = [dir for dir in ['E', 'W', 'N', 'S'] 
                            if j1_data[f'{dir}_halting'] > 0 or j1_data[f'{dir}_total'] > 0]
        print(f"  Visible Directions: {visible_directions}")

if __name__ == "__main__":
    demonstrate_rotation()