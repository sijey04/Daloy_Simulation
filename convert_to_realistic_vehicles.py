#!/usr/bin/env python3
"""
Convert KCCIntersection_realistic.rou.xml to use authentic Filipino vehicle types
Based on actual traffic distribution in Zamboanga City KCC area
"""

import random
import re

def convert_to_realistic_vehicles():
    """Convert the route file to use realistic Filipino vehicle types"""
    
    # Read the current file
    with open('KCCIntersection_realistic.rou.xml', 'r') as f:
        content = f.read()
    
    # Define realistic vehicle distribution for Zamboanga City KCC
    vehicle_types = [
        ('jeepney', 40),        # 40% - Main public transport
        ('tricycle', 25),       # 25% - Local transport
        ('private_car', 15),    # 15% - Private vehicles
        ('multicab', 10),       # 10% - Small utility vehicles
        ('delivery_truck', 5),  # 5% - Commercial vehicles
        ('habal_habal', 3),     # 3% - Motorcycle taxis
        ('bus', 2),             # 2% - Public buses
    ]
    
    # Create weighted list for random selection
    weighted_types = []
    for vtype, weight in vehicle_types:
        weighted_types.extend([vtype] * weight)
    
    # Counter for each vehicle type
    type_counters = {vtype: 1 for vtype, _ in vehicle_types}
    
    # Find all vehicle definitions with generic IDs (numbers)
    pattern = r'<vehicle id="(\d+)" depart="([^"]+)">'
    matches = re.findall(pattern, content)
    
    print(f"🚗 Converting {len(matches)} vehicles to realistic Filipino types...")
    
    # Replace each generic vehicle with realistic type
    for old_id, depart_time in matches:
        # Select random vehicle type based on distribution
        selected_type = random.choice(weighted_types)
        
        # Create new ID with type prefix
        new_id = f"{selected_type}_{type_counters[selected_type]:04d}"
        type_counters[selected_type] += 1
        
        # Replace in content
        old_pattern = f'<vehicle id="{old_id}" depart="{depart_time}">'
        new_pattern = f'<vehicle id="{new_id}" type="{selected_type}" depart="{depart_time}">'
        content = content.replace(old_pattern, new_pattern)
    
    # Write the updated file
    with open('KCCIntersection_realistic.rou.xml', 'w') as f:
        f.write(content)
    
    # Print statistics
    print("\n✅ ZAMBOANGA CITY KCC REALISTIC VEHICLE CONVERSION COMPLETE!")
    print("=" * 60)
    print("Vehicle Distribution Summary:")
    for vtype, expected_percent in vehicle_types:
        actual_count = type_counters[vtype] - 1  # Subtract 1 because we start at 1
        print(f"  • {vtype.upper():<15}: {actual_count:4d} vehicles ({expected_percent}%)")
    
    total_vehicles = sum(type_counters[vtype] - 1 for vtype, _ in vehicle_types)
    print(f"\nTotal Realistic Vehicles: {total_vehicles}")
    print("\nAuthentic Filipino Vehicle Types:")
    print("  🚌 Jeepneys: Main public transport (colorful, iconic)")
    print("  🛵 Tricycles: Local short-distance transport")
    print("  🚐 Multicabs: Small utility vehicles")
    print("  🚗 Private Cars: Sedans, SUVs")
    print("  🚛 Delivery Trucks: Commercial cargo")
    print("  🏍️ Habal-habal: Motorcycle taxis")
    print("  🚍 Buses: Public long-distance transport")

if __name__ == "__main__":
    # Set random seed for consistent results
    random.seed(2025)
    convert_to_realistic_vehicles()