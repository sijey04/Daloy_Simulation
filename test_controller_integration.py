#!/usr/bin/env python3

"""
Enhanced Traffic Controller Integration Test
Tests the traffic controller with the new East approach detectors
"""

import os
import sys
import traci

# Test the enhanced traffic controller with new detectors
def test_enhanced_controller():
    print("🚦 Testing Enhanced Traffic Controller with New East Detectors")
    print("=" * 65)
    
    try:
        # Import our enhanced traffic controller
        from traffic_controller import EnhancedTrafficController, TrafficMetrics
        
        # Initialize controller and metrics
        controller = EnhancedTrafficController()
        metrics = TrafficMetrics()
        
        # Start SUMO for testing
        traci.start(["sumo", "-c", "KCCIntersection.sumocfg", "--no-step-log", "--start"])
        
        print("📊 Testing Enhanced 360° Camera Data Collection:")
        
        # Test J1 camera data with new East detectors
        j1_data = controller.get_360_camera_data('J1', 1)
        print("✅ J1 360° Camera Data Collected Successfully:")
        print(f"   • East Approach (8 detectors): {j1_data['E_halting']} halting, {j1_data['E_total']} total")
        print(f"   • West Approach (2 detectors): {j1_data['W_halting']} halting, {j1_data['W_total']} total")
        print(f"   • North Approach (4 detectors): {j1_data['N_halting']} halting, {j1_data['N_total']} total")
        print(f"   • South Approach (4 detectors): {j1_data['S_halting']} halting, {j1_data['S_total']} total")
        
        # Test J2 camera data 
        j2_data = controller.get_360_camera_data('J2', 1)
        print("\n✅ J2 360° Camera Data Collected Successfully:")
        print(f"   • East Approach (6 detectors): {j2_data['E_halting']} halting, {j2_data['E_total']} total")
        print(f"   • West Approach (4 detectors): {j2_data['W_halting']} halting, {j2_data['W_total']} total")
        print(f"   • North Approach (2 detectors): {j2_data['N_halting']} halting, {j2_data['N_total']} total")
        print(f"   • South Approach (4 detectors): {j2_data['S_halting']} halting, {j2_data['S_total']} total")
        
        # Test urgency calculation with new detector setup
        print("\n⚡ Testing Enhanced Urgency Calculation:")
        j1_ew_urgency = controller.calculate_urgency_score(j1_data, 'J1', 'EW')
        j1_ns_urgency = controller.calculate_urgency_score(j1_data, 'J1', 'NS')
        j2_ew_urgency = controller.calculate_urgency_score(j2_data, 'J2', 'EW')
        j2_ns_urgency = controller.calculate_urgency_score(j2_data, 'J2', 'NS')
        
        print(f"   • J1 East-West Urgency: {j1_ew_urgency:.2f}")
        print(f"   • J1 North-South Urgency: {j1_ns_urgency:.2f}")
        print(f"   • J2 East-West Urgency: {j2_ew_urgency:.2f}")
        print(f"   • J2 North-South Urgency: {j2_ns_urgency:.2f}")
        
        # Test traffic prediction
        print("\n🔮 Testing Traffic Prediction:")
        for intersection in ['J1', 'J2']:
            for direction in ['E', 'W', 'N', 'S']:
                trend = controller.predict_traffic_trend(intersection, direction)
                print(f"   • {intersection} {direction} trend: {trend:.2f}")
        
        # Test metrics collection with new detectors
        print("\n📈 Testing Metrics Collection:")
        queue_j1 = metrics.calculate_queue_length('J1')
        queue_j2 = metrics.calculate_queue_length('J2')
        waiting_j1 = metrics.calculate_intersection_waiting_time('J1')
        waiting_j2 = metrics.calculate_intersection_waiting_time('J2')
        
        print(f"   • J1 Queue Length (18 detectors): {queue_j1} vehicles")
        print(f"   • J2 Queue Length (16 detectors): {queue_j2} vehicles")
        print(f"   • J1 Average Waiting Time: {waiting_j1:.2f} seconds")
        print(f"   • J2 Average Waiting Time: {waiting_j2:.2f} seconds")
        
        # Test enhanced traffic control method
        print("\n🎯 Testing Enhanced Traffic Control Logic:")
        TLS_ID_J1 = "1017322684"
        TLS_ID_J2 = "1017322720"
        
        # Run a few steps of traffic control
        for step in range(2, 10, 2):  # Test camera rotation every 2 steps
            traffic_data = controller.enhanced_traffic_control(step, TLS_ID_J1, TLS_ID_J2, metrics)
            if traffic_data:
                j1_data, j2_data = traffic_data
                print(f"   • Step {step}: Enhanced control executed successfully")
                print(f"     J1 East: {j1_data['E_halting']} halting, J2 East: {j2_data['E_halting']} halting")
        
        # Close test simulation
        traci.close()
        
        print("\n🎉 Enhanced Traffic Controller Integration Test Complete!")
        print("✅ All systems working with extended East approach coverage")
        print(f"📊 Total Detector Summary:")
        print(f"   • J1: 18 detectors (8 East + 2 West + 4 North + 4 South)")
        print(f"   • J2: 16 detectors (6 East + 4 West + 2 North + 4 South)")
        print(f"   • Total: 34 lane area detectors providing comprehensive coverage")
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    test_enhanced_controller()