#!/usr/bin/env python3
"""
Create a clean realistic route file with proper Filipino vehicle types
"""

def create_clean_realistic_routes():
    # Read original file to get route patterns
    with open('KCCIntersection_500h.rou.xml', 'r') as f:
        content = f.read()
    
    # Extract all unique routes
    import re
    
    # Find all vehicle entries
    vehicle_pattern = r'<vehicle id="[^"]*" (?:type="[^"]*" )?depart="([^"]*)">\s*<route edges="([^"]*)"/>\s*</vehicle>'
    vehicles = re.findall(vehicle_pattern, content, re.MULTILINE | re.DOTALL)
    
    print(f"Found {len(vehicles)} vehicle entries")
    
    # Define realistic vehicle distribution
    vehicle_types = [
        ('jeepney', 40),        # 40% - Main public transport
        ('tricycle', 25),       # 25% - Local transport  
        ('private_car', 15),    # 15% - Private vehicles
        ('multicab', 10),       # 10% - Small utility vehicles
        ('delivery_truck', 5),  # 5% - Commercial vehicles
        ('habal_habal', 3),     # 3% - Motorcycle taxis
        ('bus', 2),             # 2% - Public buses
    ]
    
    # Create weighted selection
    import random
    random.seed(2025)
    
    weighted_types = []
    for vtype, weight in vehicle_types:
        weighted_types.extend([vtype] * weight)
    
    # Generate clean route file
    header = '''<?xml version="1.0" encoding="UTF-8"?>

<!-- REALISTIC ZAMBOANGA CITY KCC VEHICLE TYPES -->
<!-- Generated with authentic Filipino vehicle distribution -->

<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    
    <!-- ZAMBOANGA CITY KCC REALISTIC VEHICLE TYPES -->
    <!-- Based on actual traffic composition in KCC area -->
    
    <!-- JEEPNEYS - Most common public transport (40% of traffic) -->
    <vType id="jeepney" accel="1.5" decel="3.5" sigma="0.8" length="7.0" width="2.2" 
           minGap="1.5" maxSpeed="20.0" speedFactor="0.9" color="1,0.8,0" 
           vClass="passenger" carFollowModel="Krauss"/>
    
    <!-- TRICYCLES - Very common local transport (25% of traffic) -->
    <vType id="tricycle" accel="2.0" decel="4.0" sigma="0.9" length="3.5" width="1.8" 
           minGap="1.0" maxSpeed="15.0" speedFactor="0.8" color="0,0.7,1" 
           vClass="motorcycle" carFollowModel="Krauss"/>
    
    <!-- MULTICABS - Small utility vehicles (10% of traffic) -->
    <vType id="multicab" accel="1.8" decel="3.0" sigma="0.7" length="4.5" width="1.9" 
           minGap="1.2" maxSpeed="18.0" speedFactor="0.85" color="0.8,0.4,0" 
           vClass="passenger" carFollowModel="Krauss"/>
    
    <!-- PRIVATE CARS - Sedans, SUVs (15% of traffic) -->
    <vType id="private_car" accel="2.5" decel="4.5" sigma="0.5" length="4.8" width="1.8" 
           minGap="2.0" maxSpeed="25.0" speedFactor="1.0" color="0.2,0.2,0.8" 
           vClass="passenger" carFollowModel="Krauss"/>
    
    <!-- DELIVERY TRUCKS - Small cargo vehicles (5% of traffic) -->
    <vType id="delivery_truck" accel="1.2" decel="3.0" sigma="0.6" length="6.5" width="2.3" 
           minGap="2.5" maxSpeed="22.0" speedFactor="0.9" color="0.6,0.6,0.6" 
           vClass="truck" carFollowModel="Krauss"/>
    
    <!-- HABAL-HABAL - Motorcycle taxis (3% of traffic) -->
    <vType id="habal_habal" accel="3.0" decel="5.0" sigma="1.0" length="2.2" width="0.8" 
           minGap="0.8" maxSpeed="25.0" speedFactor="1.1" color="1,0,0" 
           vClass="motorcycle" carFollowModel="Krauss"/>
    
    <!-- BUSES - Public buses (2% of traffic) -->
    <vType id="bus" accel="1.0" decel="2.5" sigma="0.4" length="12.0" width="2.5" 
           minGap="3.0" maxSpeed="20.0" speedFactor="0.8" color="0,1,0" 
           vClass="bus" carFollowModel="Krauss"/>

    <!-- REALISTIC TRAFFIC ROUTES WITH ZAMBOANGA VEHICLE TYPES -->

'''
    
    # Counter for each vehicle type
    type_counters = {vtype: 1 for vtype, _ in vehicle_types}
    
    vehicle_entries = []
    
    # Generate vehicles with realistic types
    for i, (depart_time, route_edges) in enumerate(vehicles):
        # Select random vehicle type based on distribution
        selected_type = random.choice(weighted_types)
        
        # Create unique ID
        vehicle_id = f"{selected_type}_{type_counters[selected_type]:04d}"
        type_counters[selected_type] += 1
        
        # Create vehicle entry
        vehicle_entry = f'    <vehicle id="{vehicle_id}" type="{selected_type}" depart="{depart_time}">\n'
        vehicle_entry += f'        <route edges="{route_edges}"/>\n'
        vehicle_entry += '    </vehicle>'
        
        vehicle_entries.append(vehicle_entry)
    
    footer = '\n</routes>\n'
    
    # Write clean file
    with open('KCCIntersection_realistic.rou.xml', 'w') as f:
        f.write(header)
        f.write('\n'.join(vehicle_entries))
        f.write(footer)
    
    # Print statistics
    print("\n✅ CLEAN ZAMBOANGA CITY KCC VEHICLE FILE CREATED!")
    print("=" * 55)
    print("Vehicle Distribution Summary:")
    for vtype, expected_percent in vehicle_types:
        actual_count = type_counters[vtype] - 1
        actual_percent = (actual_count / len(vehicles)) * 100
        print(f"  • {vtype.upper():<15}: {actual_count:4d} vehicles ({actual_percent:.1f}%)")
    
    print(f"\nTotal Vehicles: {len(vehicles)}")
    print("🇵🇭 Authentic Filipino Traffic for KCC Zamboanga!")

if __name__ == "__main__":
    create_clean_realistic_routes()