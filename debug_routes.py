#!/usr/bin/env python3
"""
Route File and Network Compatibility Checker
"""

import xml.etree.ElementTree as ET
import os

def check_files():
    print('=' * 60)
    print('COMPREHENSIVE ROUTE AND NETWORK ANALYSIS')
    print('=' * 60)
    
    print('\n1. FILE EXISTENCE CHECK:')
    files_to_check = [
        'KCCIntersection.net.xml',
        'KCCIntersection_busy_24hour.rou.xml',
        'KCCIntersectionConfig.add.xml'
    ]

    for file in files_to_check:
        exists = os.path.exists(file)
        size = os.path.getsize(file) if exists else 0
        print(f'   {file}: {"EXISTS" if exists else "MISSING"} ({size} bytes)')

    print('\n2. ROUTE FILE ANALYSIS:')
    try:
        tree = ET.parse('KCCIntersection_busy_24hour.rou.xml')
        root = tree.getroot()
        vehicles = root.findall('vehicle')
        print(f'   Total vehicles: {len(vehicles)}')
        
        if vehicles:
            print(f'\n   First 5 vehicles:')
            for i, v in enumerate(vehicles[:5]):
                route = v.find('route')
                edges = route.get('edges') if route is not None else 'NO ROUTE'
                print(f'     {i+1}. ID: {v.get("id")}, Depart: {v.get("depart")}s')
                print(f'        Route: {edges}')
            
            # Check departure time distribution
            departure_times = sorted([float(v.get('depart', 0)) for v in vehicles])
            print(f'\n   Departure time analysis:')
            print(f'     Range: {departure_times[0]:.1f}s to {departure_times[-1]:.1f}s')
            print(f'     First 10: {[f"{t:.1f}" for t in departure_times[:10]]}')
            
            # Check if vehicles depart early enough
            early_vehicles = [t for t in departure_times if t < 3600]  # First hour
            very_early = [t for t in departure_times if t < 600]  # First 10 minutes
            print(f'     Vehicles in first hour: {len(early_vehicles)}')
            print(f'     Vehicles in first 10 minutes: {len(very_early)}')
            
    except Exception as e:
        print(f'   ERROR parsing route file: {e}')

    print('\n3. NETWORK FILE CHECK:')
    try:
        tree = ET.parse('KCCIntersection.net.xml')
        root = tree.getroot()
        edges = root.findall('edge')
        print(f'   Total edges in network: {len(edges)}')
        
        # Get all edge IDs
        edge_ids = set(edge.get('id') for edge in edges)
        print(f'   Sample edge IDs: {list(edge_ids)[:10]}')
        
        # Check route compatibility
        route_tree = ET.parse('KCCIntersection_busy_24hour.rou.xml')
        route_root = route_tree.getroot()
        first_vehicle = route_root.find('vehicle')
        
        if first_vehicle is not None:
            route_elem = first_vehicle.find('route')
            if route_elem is not None:
                route_edges = route_elem.get('edges').split()
                print(f'\n   Route compatibility check:')
                print(f'     First vehicle route: {route_edges}')
                
                missing_edges = [e for e in route_edges if e not in edge_ids]
                if missing_edges:
                    print(f'     ❌ MISSING EDGES: {missing_edges}')
                    print(f'     Available edges containing similar patterns:')
                    for missing in missing_edges:
                        similar = [e for e in edge_ids if missing[:5] in e or e[:5] in missing]
                        print(f'       {missing} -> Similar: {similar[:5]}')
                else:
                    print(f'     ✅ All route edges exist in network')
                    
    except Exception as e:
        print(f'   ERROR checking network: {e}')

    print('\n4. CREATING IMMEDIATE VISIBILITY ROUTE:')
    # Create a route with vehicles departing every 10 seconds for immediate visibility
    try:
        immediate_route_content = '''<?xml version='1.0' encoding='UTF-8'?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <!-- Filipino Vehicle Types -->
    <vType id="jeepney" accel="1.5" decel="3.5" sigma="0.8" length="7.0" width="2.2" minGap="2.5" maxSpeed="25.0" speedFactor="0.9" color="1,1,0" vClass="passenger" carFollowModel="Krauss" />
    <vType id="tricycle" accel="2.0" decel="4.0" sigma="0.9" length="3.5" width="1.8" minGap="2.0" maxSpeed="20.0" speedFactor="0.8" color="1,0,1" vClass="motorcycle" carFollowModel="Krauss" />
    <vType id="private_car" accel="2.5" decel="4.5" sigma="0.5" length="4.8" width="1.8" minGap="2.0" maxSpeed="30.0" speedFactor="1.0" color="0,0,1" vClass="passenger" carFollowModel="Krauss" />

    <!-- IMMEDIATE VISIBILITY TEST VEHICLES (Every 10 seconds) -->'''
        
        # Add vehicles every 10 seconds for the first 5 minutes
        vehicle_types = ['jeepney', 'tricycle', 'private_car']
        
        # Get available routes from the network
        net_tree = ET.parse('KCCIntersection.net.xml')
        net_root = net_tree.getroot()
        edges = [edge.get('id') for edge in net_root.findall('edge') if not edge.get('id').startswith(':')]
        
        if len(edges) >= 4:
            # Create simple routes using available edges
            routes = [
                f"{edges[0]} {edges[1]}",
                f"{edges[2]} {edges[3]}" if len(edges) > 3 else f"{edges[0]} {edges[1]}",
                f"{edges[1]} {edges[0]}" if len(edges) > 1 else edges[0]
            ]
            
            for i in range(30):  # 30 vehicles over 5 minutes
                depart_time = i * 10  # Every 10 seconds
                vehicle_type = vehicle_types[i % 3]
                route = routes[i % len(routes)]
                
                immediate_route_content += f'''
    <vehicle id="{vehicle_type}_{i+1:04d}" type="{vehicle_type}" depart="{depart_time}">
        <route edges="{route}" />
    </vehicle>'''
        
        immediate_route_content += '''
</routes>'''
        
        # Save immediate visibility route
        with open('KCCIntersection_immediate_test.rou.xml', 'w') as f:
            f.write(immediate_route_content)
        
        print(f'   ✅ Created immediate test route: KCCIntersection_immediate_test.rou.xml')
        print(f'   Contains 30 vehicles departing every 10 seconds')
        
    except Exception as e:
        print(f'   ❌ Error creating immediate route: {e}')

    print('\n' + '=' * 60)
    print('DIAGNOSIS COMPLETE')
    print('=' * 60)

if __name__ == "__main__":
    check_files()