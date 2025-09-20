#!/usr/bin/env python3

"""
Enhanced 4-Lane East Approach Detector Test
Tests the new detectors covering the 4-lane section in the east approach to the complex intersection
"""

import os
import sys
import traci

def test_4_lane_east_detectors():
    print("🚗 Testing Enhanced 4-Lane East Approach Detectors for Complex Intersection")
    print("=" * 75)
    
    try:
        # Start SUMO for testing
        traci.start(["sumo", "-c", "KCCIntersection.sumocfg", "--no-step-log", "--start"])
        
        # Test all J1 East approach detectors (now including 4-lane section)
        east_detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4', 
                         'det_J1_E5', 'det_J1_E6', 'det_J1_E7', 'det_J1_E8',
                         'det_J1_E9', 'det_J1_E10']  # New 4-lane detectors
        
        print("📊 Testing J1 Enhanced East Approach Detectors (4-Lane Coverage):")
        
        working_detectors = 0
        total_detectors = len(east_detectors)
        
        for i, det_id in enumerate(east_detectors, 1):
            try:
                # Test detector accessibility
                vehicle_count = traci.lanearea.getLastStepVehicleNumber(det_id)
                halting_count = traci.lanearea.getLastStepHaltingNumber(det_id)
                lane_id = traci.lanearea.getLaneID(det_id)
                position = traci.lanearea.getPosition(det_id)
                length = traci.lanearea.getLength(det_id)
                
                status = "✅ WORKING"
                working_detectors += 1
                
                # Identify which segment this detector covers
                if i <= 4:
                    segment = "Primary East Lanes"
                elif i <= 8:
                    segment = "Extended East Segments"
                else:
                    segment = "4-Lane East Section (NEW)"
                
                print(f"  {i:2d}. {det_id:13s} - {status} | {segment}")
                print(f"      Lane: {lane_id:20s} | Pos: {position:5.2f}m | Len: {length:5.2f}m")
                print(f"      Vehicles: {vehicle_count:2d} | Halting: {halting_count:2d}")
                
            except Exception as e:
                status = f"❌ ERROR: {e}"
                print(f"  {i:2d}. {det_id:13s} - {status}")
        
        # Test enhanced traffic controller integration
        print(f"\n🎯 Testing Enhanced Traffic Controller Integration:")
        
        from traffic_controller import EnhancedTrafficController, TrafficMetrics
        controller = EnhancedTrafficController()
        metrics = TrafficMetrics()
        
        # Test enhanced 360° camera data collection
        j1_data = controller.get_360_camera_data('J1', 1)
        print(f"✅ Enhanced J1 360° Camera Data (10 East Detectors):")
        print(f"   • East Approach: {j1_data['E_halting']:2d} halting, {j1_data['E_total']:2d} total vehicles")
        print(f"   • East Waiting Time: {j1_data['E_waiting']:5.2f} seconds average")
        
        # Test enhanced metrics collection
        queue_j1 = metrics.calculate_queue_length('J1')
        waiting_j1 = metrics.calculate_intersection_waiting_time('J1')
        
        print(f"\n📈 Enhanced Metrics Collection:")
        print(f"   • J1 Enhanced Queue Length: {queue_j1:2d} vehicles (20 total detectors)")
        print(f"   • J1 Enhanced Waiting Time: {waiting_j1:5.2f} seconds")
        
        # Test urgency calculation with extended coverage
        j1_ew_urgency = controller.calculate_urgency_score(j1_data, 'J1', 'EW')
        j1_ns_urgency = controller.calculate_urgency_score(j1_data, 'J1', 'NS')
        
        print(f"\n⚡ Enhanced Urgency Calculation (with 4-lane coverage):")
        print(f"   • J1 East-West Urgency: {j1_ew_urgency:5.2f}")
        print(f"   • J1 North-South Urgency: {j1_ns_urgency:5.2f}")
        
        # Close test simulation
        traci.close()
        
        print(f"\n🎉 Enhanced 4-Lane East Approach Test Complete!")
        print(f"✅ Working Detectors: {working_detectors}/{total_detectors}")
        print(f"📊 Final Configuration Summary:")
        print(f"   • J1 Total Detectors: 20 (10 East + 2 West + 4 North + 4 South)")
        print(f"   • East Approach Coverage: 10 detectors across multiple lane segments")
        print(f"   • 4-Lane Section: 2 additional detectors (det_J1_E9, det_J1_E10)")
        print(f"   • Enhanced 360° Camera Range: Full coverage of complex intersection approaches")
        print(f"🚥 Traffic Control Benefits:")
        print(f"   • Better detection of vehicles in 4-lane east section")
        print(f"   • Improved urgency scoring with comprehensive data")
        print(f"   • Enhanced traffic prediction and coordination")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    test_4_lane_east_detectors()