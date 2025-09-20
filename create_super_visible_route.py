#!/usr/bin/env python3
"""
Create VERY VISIBLE Traffic Route for Immediate Testing
"""

import xml.etree.ElementTree as ET
import random

def create_super_visible_route():
    print("🚗 CREATING SUPER VISIBLE TRAFFIC ROUTE")
    print("=" * 60)
    
    # Load network to get available edges
    try:
        net_tree = ET.parse('KCCIntersection.net.xml')
        net_root = net_tree.getroot()
        
        # Get all non-internal edges
        all_edges = []
        for edge in net_root.findall('edge'):
            edge_id = edge.get('id')
            if edge_id and not edge_id.startswith(':'):
                all_edges.append(edge_id)
        
        print(f"✅ Found {len(all_edges)} available edges in network")
        
        # Create route content
        route_content = '''<?xml version='1.0' encoding='UTF-8'?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <!-- Filipino Vehicle Types with BRIGHT COLORS for Visibility -->
    <vType id="jeepney" accel="1.5" decel="3.5" sigma="0.8" length="7.0" width="2.2" minGap="2.5" maxSpeed="25.0" speedFactor="0.9" color="1,1,0" vClass="passenger" carFollowModel="Krauss" />
    <vType id="tricycle" accel="2.0" decel="4.0" sigma="0.9" length="3.5" width="1.8" minGap="2.0" maxSpeed="20.0" speedFactor="0.8" color="1,0,1" vClass="motorcycle" carFollowModel="Krauss" />
    <vType id="private_car" accel="2.5" decel="4.5" sigma="0.5" length="4.8" width="1.8" minGap="2.0" maxSpeed="30.0" speedFactor="1.0" color="0,0,1" vClass="passenger" carFollowModel="Krauss" />
    <vType id="multicab" accel="1.8" decel="3.0" sigma="0.7" length="4.5" width="1.9" minGap="2.2" maxSpeed="22.0" speedFactor="0.85" color="0,1,1" vClass="passenger" carFollowModel="Krauss" />
    <vType id="delivery_truck" accel="1.2" decel="3.0" sigma="0.6" length="6.5" width="2.3" minGap="3.0" maxSpeed="18.0" speedFactor="0.7" color="0.5,0.5,0.5" vClass="delivery" carFollowModel="Krauss" />
    <vType id="habal_habal" accel="3.0" decel="5.0" sigma="1.0" length="2.2" width="0.8" minGap="1.5" maxSpeed="25.0" speedFactor="1.1" color="1,0.5,0" vClass="motorcycle" carFollowModel="Krauss" />
    <vType id="bus" accel="1.0" decel="2.5" sigma="0.4" length="12.0" width="2.5" minGap="3.0" maxSpeed="20.0" speedFactor="0.8" color="0,1,0" vClass="bus" carFollowModel="Krauss" />

    <!-- SUPER VISIBLE TRAFFIC - VEHICLES EVERY 15 SECONDS! -->'''
        
        # Vehicle types and their weights for realistic distribution
        vehicle_types = [
            ('jeepney', 40),      # 40% jeepneys
            ('tricycle', 25),     # 25% tricycles  
            ('private_car', 20),  # 20% private cars
            ('multicab', 8),      # 8% multicabs
            ('habal_habal', 4),   # 4% habal-habal
            ('delivery_truck', 2), # 2% delivery trucks
            ('bus', 1)           # 1% buses
        ]
        
        # Create weighted vehicle type list
        weighted_vehicles = []
        for vtype, weight in vehicle_types:
            weighted_vehicles.extend([vtype] * weight)
        
        # Create routes using available edges
        routes = []
        if len(all_edges) >= 8:
            # Create multiple route patterns
            routes = [
                f"{all_edges[0]} {all_edges[1]}",
                f"{all_edges[2]} {all_edges[3]}",
                f"{all_edges[4]} {all_edges[5]}",
                f"{all_edges[6]} {all_edges[7]}",
                f"{all_edges[1]} {all_edges[0]}",
                f"{all_edges[3]} {all_edges[2]}",
                f"{all_edges[5]} {all_edges[4]}",
                f"{all_edges[7]} {all_edges[6]}",
            ]
        elif len(all_edges) >= 4:
            routes = [
                f"{all_edges[0]} {all_edges[1]}",
                f"{all_edges[2]} {all_edges[3]}",
                f"{all_edges[1]} {all_edges[0]}",
                f"{all_edges[3]} {all_edges[2]}",
            ]
        elif len(all_edges) >= 2:
            routes = [
                f"{all_edges[0]} {all_edges[1]}",
                f"{all_edges[1]} {all_edges[0]}",
            ]
        else:
            routes = [all_edges[0]] if all_edges else ["edge1"]
        
        print(f"✅ Created {len(routes)} different route patterns")
        
        # Generate vehicles with VERY HIGH FREQUENCY
        vehicle_count = 0
        current_time = 0
        
        # PHASE 1: IMMEDIATE VISIBILITY (First 5 minutes - every 15 seconds)
        print("\n📍 Phase 1: Immediate visibility (0-5 minutes, every 15 seconds)")
        for i in range(20):  # 20 vehicles in first 5 minutes
            vehicle_type = random.choice(weighted_vehicles)
            route = random.choice(routes)
            depart_time = i * 15  # Every 15 seconds
            
            route_content += f'''
    <vehicle id="{vehicle_type}_{vehicle_count+1:04d}" type="{vehicle_type}" depart="{depart_time}">
        <route edges="{route}" />
    </vehicle>'''
            vehicle_count += 1
        
        current_time = 300  # 5 minutes
        
        # PHASE 2: SUSTAINED FLOW (5-60 minutes - every 30 seconds)
        print("📍 Phase 2: Sustained flow (5-60 minutes, every 30 seconds)")
        for i in range(110):  # 110 vehicles in next 55 minutes  
            vehicle_type = random.choice(weighted_vehicles)
            route = random.choice(routes)
            depart_time = current_time + (i * 30)  # Every 30 seconds
            
            route_content += f'''
    <vehicle id="{vehicle_type}_{vehicle_count+1:04d}" type="{vehicle_type}" depart="{depart_time}">
        <route edges="{route}" />
    </vehicle>'''
            vehicle_count += 1
        
        current_time = 3600  # 1 hour
        
        # PHASE 3: HOURLY PATTERN (Rest of 24 hours - realistic but visible)
        print("📍 Phase 3: 24-hour realistic pattern (every 1-3 minutes)")
        for hour in range(1, 24):  # Hours 1-23
            hour_start = hour * 3600
            
            # Determine vehicles per hour based on time of day
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
                vehicles_this_hour = 30  # Every 2 minutes
                interval = 120
            elif 6 <= hour <= 22:  # Daytime
                vehicles_this_hour = 20  # Every 3 minutes
                interval = 180
            else:  # Night time
                vehicles_this_hour = 10  # Every 6 minutes
                interval = 360
            
            for i in range(vehicles_this_hour):
                vehicle_type = random.choice(weighted_vehicles)
                route = random.choice(routes)
                depart_time = hour_start + (i * interval) + random.randint(0, 60)
                
                route_content += f'''
    <vehicle id="{vehicle_type}_{vehicle_count+1:04d}" type="{vehicle_type}" depart="{depart_time}">
        <route edges="{route}" />
    </vehicle>'''
                vehicle_count += 1
        
        route_content += '''
</routes>'''
        
        # Save the super visible route file
        filename = 'KCCIntersection_super_visible.rou.xml'
        with open(filename, 'w') as f:
            f.write(route_content)
        
        print(f"\n✅ SUPER VISIBLE ROUTE CREATED!")
        print(f"   📁 File: {filename}")
        print(f"   🚗 Total vehicles: {vehicle_count}")
        print(f"   ⚡ First vehicle: 0 seconds")
        print(f"   ⚡ Vehicle every 15s for first 5 minutes")
        print(f"   ⚡ Vehicle every 30s for next 55 minutes")
        print(f"   ⚡ Realistic 24-hour pattern after that")
        
        return filename, vehicle_count
        
    except Exception as e:
        print(f"❌ Error creating route: {e}")
        return None, 0

def update_configurations(route_filename):
    """Update all configuration files to use the super visible route"""
    print(f"\n🔧 UPDATING CONFIGURATION FILES")
    print("=" * 60)
    
    config_files = [
        'KCCIntersection.sumocfg',
        'KCCIntersection_optimized.sumocfg', 
        'KCCIntersection_baseline.sumocfg',
        'KCCIntersection_24hour.sumocfg'
    ]
    
    for config_file in config_files:
        try:
            # Read current config
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Update route file reference
            updated_content = content
            
            # Replace any existing route file reference
            import re
            pattern = r'<route-files value="[^"]*"/>'
            replacement = f'<route-files value="{route_filename}"/>'
            updated_content = re.sub(pattern, replacement, updated_content)
            
            # Write updated config
            with open(config_file, 'w') as f:
                f.write(updated_content)
            
            print(f"   ✅ Updated {config_file}")
            
        except Exception as e:
            print(f"   ❌ Error updating {config_file}: {e}")

if __name__ == "__main__":
    filename, count = create_super_visible_route()
    if filename:
        update_configurations(filename)
        print(f"\n🎯 READY FOR TESTING!")
        print(f"   Run any simulation - cars will appear immediately!")
        print(f"   First vehicle spawns at time 0!")
        print(f"   Continuous flow guaranteed!")