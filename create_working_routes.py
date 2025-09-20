#!/usr/bin/env python3
"""
Simple Fixed Route Generator for KCC Intersection
Creates basic working routes to prevent vehicle sticking
"""

import random
import xml.etree.ElementTree as ET

def create_simple_fixed_routes():
    print("🔧 CREATING SIMPLE WORKING ROUTES")
    print("=" * 40)
    
    # Define simple working routes that we know connect properly
    working_routes = [
        # Basic East-West
        ["276625085#0", "276625085#1", "276625085#2", "276625085#3"],
        ["-276625085#3", "-276625085#2", "-276625085#1", "-276625085#0"],
        
        # Basic North-South 
        ["824453750#0", "824453750#1", "1167494164", "276625085#0"],
        ["87479596#5", "87479596#6", "87479596#7", "824453750#0"],
        
        # Simple circulation patterns
        ["276625085#0", "276625085#1", "276625085#2", "276625085#3", "265732531"],
        ["-265732531", "-276625085#3", "-276625085#2", "-276625085#1", "-276625085#0"],
        
        # Cross patterns
        ["87479596#3", "87479596#4", "276625085#0", "276625085#1"],
        ["1167494165#1", "1167494164", "276625085#0", "276625085#1"],
        
        # Local patterns
        ["268552023#0", "268552023#1", "276625085#1", "276625085#2"],
        ["87479596#1", "87479596#2", "87479596#3", "87479596#4"],
        
        # Additional safe patterns
        ["1384034325#0", "1384034325#1", "1384034325#2", "1384034325#3"],
        ["-1384034325#3", "-1384034325#2", "-1384034325#1", "-1384034325#0"],
    ]
    
    # Filipino vehicle types
    vehicle_types = [
        ("jeepney", 0.392),      # 39.2%
        ("tricycle", 0.219),     # 21.9% 
        ("private_car", 0.186),  # 18.6%
        ("multicab", 0.100),     # 10.0%
        ("delivery_truck", 0.056), # 5.6%
        ("habal_habal", 0.031),  # 3.1%
        ("bus", 0.017)           # 1.7%
    ]
    
    # Create XML
    root = ET.Element("routes")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "http://sumo.dlr.de/xsd/routes_file.xsd")
    
    # Add vehicle types (same as before)
    jeepney_type = ET.SubElement(root, "vType")
    jeepney_type.set("id", "jeepney")
    jeepney_type.set("accel", "1.5")
    jeepney_type.set("decel", "3.5")
    jeepney_type.set("sigma", "0.8")
    jeepney_type.set("length", "7.0")
    jeepney_type.set("width", "2.2")
    jeepney_type.set("minGap", "2.5")
    jeepney_type.set("maxSpeed", "25.0")
    jeepney_type.set("speedFactor", "0.9")
    jeepney_type.set("color", "1,1,0")
    jeepney_type.set("vClass", "passenger")
    jeepney_type.set("carFollowModel", "Krauss")
    
    tricycle_type = ET.SubElement(root, "vType")
    tricycle_type.set("id", "tricycle")
    tricycle_type.set("accel", "2.0")
    tricycle_type.set("decel", "4.0")
    tricycle_type.set("sigma", "0.9")
    tricycle_type.set("length", "3.5")
    tricycle_type.set("width", "1.8")
    tricycle_type.set("minGap", "2.0")
    tricycle_type.set("maxSpeed", "20.0")
    tricycle_type.set("speedFactor", "0.8")
    tricycle_type.set("color", "1,0,1")
    tricycle_type.set("vClass", "motorcycle")
    tricycle_type.set("carFollowModel", "Krauss")
    
    car_type = ET.SubElement(root, "vType")
    car_type.set("id", "private_car")
    car_type.set("accel", "2.5")
    car_type.set("decel", "4.5")
    car_type.set("sigma", "0.5")
    car_type.set("length", "4.8")
    car_type.set("width", "1.8")
    car_type.set("minGap", "2.0")
    car_type.set("maxSpeed", "30.0")
    car_type.set("speedFactor", "1.0")
    car_type.set("color", "0,0,1")
    car_type.set("vClass", "passenger")
    car_type.set("carFollowModel", "Krauss")
    
    multicab_type = ET.SubElement(root, "vType")
    multicab_type.set("id", "multicab")
    multicab_type.set("accel", "1.8")
    multicab_type.set("decel", "3.0")
    multicab_type.set("sigma", "0.7")
    multicab_type.set("length", "4.5")
    multicab_type.set("width", "1.9")
    multicab_type.set("minGap", "2.2")
    multicab_type.set("maxSpeed", "22.0")
    multicab_type.set("speedFactor", "0.85")
    multicab_type.set("color", "0,1,1")
    multicab_type.set("vClass", "passenger")
    multicab_type.set("carFollowModel", "Krauss")
    
    truck_type = ET.SubElement(root, "vType")
    truck_type.set("id", "delivery_truck")
    truck_type.set("accel", "1.2")
    truck_type.set("decel", "3.0")
    truck_type.set("sigma", "0.6")
    truck_type.set("length", "6.5")
    truck_type.set("width", "2.3")
    truck_type.set("minGap", "3.0")
    truck_type.set("maxSpeed", "18.0")
    truck_type.set("speedFactor", "0.7")
    truck_type.set("color", "0.5,0.5,0.5")
    truck_type.set("vClass", "delivery")
    truck_type.set("carFollowModel", "Krauss")
    
    habal_type = ET.SubElement(root, "vType")
    habal_type.set("id", "habal_habal")
    habal_type.set("accel", "3.0")
    habal_type.set("decel", "5.0")
    habal_type.set("sigma", "1.0")
    habal_type.set("length", "2.2")
    habal_type.set("width", "0.8")
    habal_type.set("minGap", "1.5")
    habal_type.set("maxSpeed", "25.0")
    habal_type.set("speedFactor", "1.1")
    habal_type.set("color", "1,0.5,0")
    habal_type.set("vClass", "motorcycle")
    habal_type.set("carFollowModel", "Krauss")
    
    bus_type = ET.SubElement(root, "vType")
    bus_type.set("id", "bus")
    bus_type.set("accel", "1.0")
    bus_type.set("decel", "2.5")
    bus_type.set("sigma", "0.4")
    bus_type.set("length", "12.0")
    bus_type.set("width", "2.5")
    bus_type.set("minGap", "3.0")
    bus_type.set("maxSpeed", "20.0")
    bus_type.set("speedFactor", "0.8")
    bus_type.set("color", "0,1,0")
    bus_type.set("vClass", "bus")
    bus_type.set("carFollowModel", "Krauss")
    
    # Generate 120 vehicles (smaller number for testing)
    num_vehicles = 120
    
    # Calculate counts
    type_counts = {}
    for vtype, ratio in vehicle_types:
        type_counts[vtype] = int(num_vehicles * ratio)
    
    total_assigned = sum(type_counts.values())
    if total_assigned < num_vehicles:
        type_counts["jeepney"] += num_vehicles - total_assigned
    
    print(f"🚗 Generating {num_vehicles} vehicles:")
    for vtype, count in type_counts.items():
        print(f"  {vtype}: {count} vehicles")
    
    # Create vehicles
    vehicle_id = 1
    depart_time = 0.0
    
    for vtype, count in type_counts.items():
        for i in range(count):
            # Select a random working route
            route_edges = random.choice(working_routes).copy()
            
            vehicle = ET.SubElement(root, "vehicle")
            vehicle.set("id", f"{vtype}_{vehicle_id:04d}")
            vehicle.set("type", vtype)
            vehicle.set("depart", f"{depart_time:.2f}")
            
            route = ET.SubElement(vehicle, "route")
            route.set("edges", " ".join(route_edges))
            
            vehicle_id += 1
            depart_time += 15.0  # 15 second intervals
    
    # Write file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write("KCCIntersection_working.rou.xml", encoding="UTF-8", xml_declaration=True)
    
    print(f"✅ Created {num_vehicles} vehicles with working routes")
    print(f"📁 Saved as: KCCIntersection_working.rou.xml")

if __name__ == "__main__":
    create_simple_fixed_routes()