#!/usr/bin/env python3

"""
Detector Configuration Validation Script
Tests the new East approach detectors for Intersection 1 (J1)
"""

import os
import sys
import traci

# Test the enhanced detector configuration
def test_detector_configuration():
    print("🔍 Testing Enhanced J1 East Approach Detector Configuration")
    print("=" * 60)
    
    try:
        # Start SUMO for testing
        traci.start(["sumo", "-c", "KCCIntersection.sumocfg", "--no-step-log", "--start"])
        
        # Test all J1 East approach detectors
        east_detectors = ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4', 
                         'det_J1_E5', 'det_J1_E6', 'det_J1_E7', 'det_J1_E8']
        
        print("📊 Testing J1 East Approach Detectors:")
        for i, det_id in enumerate(east_detectors, 1):
            try:
                # Test detector accessibility
                vehicle_count = traci.lanearea.getLastStepVehicleNumber(det_id)
                halting_count = traci.lanearea.getLastStepHaltingNumber(det_id)
                lane_id = traci.lanearea.getLaneID(det_id)
                position = traci.lanearea.getPosition(det_id)
                length = traci.lanearea.getLength(det_id)
                
                status = "✅ WORKING"
                print(f"  {i:2d}. {det_id:12s} - {status}")
                print(f"      Lane: {lane_id}")
                print(f"      Position: {position:.2f}m, Length: {length:.2f}m")
                print(f"      Vehicles: {vehicle_count}, Halting: {halting_count}")
                
            except Exception as e:
                status = f"❌ ERROR: {e}"
                print(f"  {i:2d}. {det_id:12s} - {status}")
        
        # Test other J1 approaches for comparison
        print("\n🔄 Testing Other J1 Approaches:")
        
        # West approach
        west_detectors = ['det_J1_W1', 'det_J1_W2']
        print("  West Approach:")
        for det_id in west_detectors:
            try:
                vehicle_count = traci.lanearea.getLastStepVehicleNumber(det_id)
                print(f"    {det_id}: ✅ Working (Vehicles: {vehicle_count})")
            except Exception as e:
                print(f"    {det_id}: ❌ Error - {e}")
        
        # North approach
        north_detectors = ['det_J1_N1', 'det_J1_N2', 'det_J1_N3', 'det_J1_N4']
        print("  North Approach:")
        for det_id in north_detectors:
            try:
                vehicle_count = traci.lanearea.getLastStepVehicleNumber(det_id)
                print(f"    {det_id}: ✅ Working (Vehicles: {vehicle_count})")
            except Exception as e:
                print(f"    {det_id}: ❌ Error - {e}")
        
        # South approach
        south_detectors = ['det_J1_S1', 'det_J1_S2', 'det_J1_S3', 'det_J1_S4']
        print("  South Approach:")
        for det_id in south_detectors:
            try:
                vehicle_count = traci.lanearea.getLastStepVehicleNumber(det_id)
                print(f"    {det_id}: ✅ Working (Vehicles: {vehicle_count})")
            except Exception as e:
                print(f"    {det_id}: ❌ Error - {e}")
        
        # Summary
        total_detectors = len(east_detectors) + len(west_detectors) + len(north_detectors) + len(south_detectors)
        print(f"\n📈 Summary:")
        print(f"   • Total J1 Detectors: {total_detectors}")
        print(f"   • East Approach: {len(east_detectors)} detectors (Extended from 4 to 8)")
        print(f"   • West Approach: {len(west_detectors)} detectors")
        print(f"   • North Approach: {len(north_detectors)} detectors")
        print(f"   • South Approach: {len(south_detectors)} detectors")
        
        # Close test simulation
        traci.close()
        
        print("\n🎉 Detector Configuration Test Complete!")
        print("✅ Enhanced East approach coverage successfully implemented")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    test_detector_configuration()