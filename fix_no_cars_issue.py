#!/usr/bin/env python3
"""
Fix the 'no cars' issue in both baseline and optimized simulations
"""
import xml.etree.ElementTree as ET
import random

def create_busy_traffic_route_file():
    """Create a route file with continuous traffic that maintains realistic patterns"""
    
    print("🚗 CREATING BUSY TRAFFIC ROUTE FILE...")
    
    # Base routes (working routes from previous analysis)
    base_routes = [
        "1167494165#1 1167494164 276625085#0 276625085#1",
        "87479596#5 87479596#6 87479596#7 824453750#0", 
        "-276625085#3 -276625085#2 -276625085#1 -276625085#0",
        "87479596#3 87479596#4 276625085#0 276625085#1",
        "87479596#1 87479596#2 87479596#3 87479596#4",
        "1384034325#0 1384034325#1 1384034325#2 1384034325#3",
        "276625085#0 276625085#1 276625085#2 276625085#3 265732531",
        "-265732531 -276625085#3 -276625085#2 -276625085#1 -276625085#0",
        "268552023#0 268552023#1 276625085#1 276625085#2",
        "824453750#0 824453750#1 1167494164 276625085#0"
    ]
    
    # Traffic intensity by hour (0-23) - realistic but with enough cars
    traffic_intensity = {
        # Night hours (fewer cars but still visible)
        0: 2, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2,
        # Early morning buildup
        6: 4,
        # Morning rush (peak traffic)
        7: 8, 8: 8, 9: 6,
        # Midday (moderate traffic)
        10: 5, 11: 5, 12: 6, 13: 5, 14: 5, 15: 5, 16: 6,
        # Evening rush (peak traffic)
        17: 8, 18: 8, 19: 6,
        # Evening decline
        20: 4, 21: 3, 22: 3, 23: 2
    }
    
    # Vehicle type distributions
    vehicle_distributions = {
        'rush_hour': {
            'jeepney': 0.35, 'tricycle': 0.15, 'private_car': 0.25, 
            'multicab': 0.10, 'delivery_truck': 0.05, 'habal_habal': 0.05, 'bus': 0.05
        },
        'normal_hour': {
            'jeepney': 0.40, 'tricycle': 0.20, 'private_car': 0.20, 
            'multicab': 0.10, 'delivery_truck': 0.05, 'habal_habal': 0.03, 'bus': 0.02
        },
        'night_hour': {
            'jeepney': 0.30, 'tricycle': 0.25, 'private_car': 0.30, 
            'multicab': 0.10, 'delivery_truck': 0.03, 'habal_habal': 0.02, 'bus': 0.00
        }
    }
    
    # Create XML content
    xml_content = '''<?xml version='1.0' encoding='UTF-8'?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <!-- Filipino Vehicle Types with Realistic Parameters -->
    <vType id="jeepney" accel="1.5" decel="3.5" sigma="0.8" length="7.0" width="2.2" minGap="2.5" maxSpeed="25.0" speedFactor="0.9" color="1,1,0" vClass="passenger" carFollowModel="Krauss" />
    <vType id="tricycle" accel="2.0" decel="4.0" sigma="0.9" length="3.5" width="1.8" minGap="2.0" maxSpeed="20.0" speedFactor="0.8" color="1,0,1" vClass="motorcycle" carFollowModel="Krauss" />
    <vType id="private_car" accel="2.5" decel="4.5" sigma="0.5" length="4.8" width="1.8" minGap="2.0" maxSpeed="30.0" speedFactor="1.0" color="0,0,1" vClass="passenger" carFollowModel="Krauss" />
    <vType id="multicab" accel="1.8" decel="3.0" sigma="0.7" length="4.5" width="1.9" minGap="2.2" maxSpeed="22.0" speedFactor="0.85" color="0,1,1" vClass="passenger" carFollowModel="Krauss" />
    <vType id="delivery_truck" accel="1.2" decel="3.0" sigma="0.6" length="6.5" width="2.3" minGap="3.0" maxSpeed="18.0" speedFactor="0.7" color="0.5,0.5,0.5" vClass="delivery" carFollowModel="Krauss" />
    <vType id="habal_habal" accel="3.0" decel="5.0" sigma="1.0" length="2.2" width="0.8" minGap="1.5" maxSpeed="25.0" speedFactor="1.1" color="1,0.5,0" vClass="motorcycle" carFollowModel="Krauss" />
    <vType id="bus" accel="1.0" decel="2.5" sigma="0.4" length="12.0" width="2.5" minGap="3.0" maxSpeed="20.0" speedFactor="0.8" color="0,1,0" vClass="bus" carFollowModel="Krauss" />

    <!-- BUSY 24-HOUR TRAFFIC with CONTINUOUS FLOW -->
'''
    
    vehicle_id = 1
    
    # Generate vehicles for 24 hours with continuous flow
    for hour in range(24):
        hour_start = hour * 3600
        vehicles_this_hour = traffic_intensity[hour]
        
        # Determine vehicle distribution for this hour
        if hour in [7, 8, 17, 18]:  # Rush hours
            dist = vehicle_distributions['rush_hour']
        elif hour >= 0 and hour <= 5:  # Night hours
            dist = vehicle_distributions['night_hour'] 
        else:  # Normal hours
            dist = vehicle_distributions['normal_hour']
        
        # Generate vehicles throughout the hour (not just at the start)
        for v in range(vehicles_this_hour):
            # Spread vehicles throughout the hour (every 3-10 minutes)
            if vehicles_this_hour > 0:
                time_gap = 3600 / vehicles_this_hour  # Base gap
                random_offset = random.uniform(-time_gap/3, time_gap/3)  # Add randomness
                departure_time = hour_start + (v * time_gap) + random_offset
                departure_time = max(0, departure_time)  # Ensure positive
            else:
                departure_time = hour_start
            
            # Select vehicle type based on distribution
            rand = random.random()
            cumulative = 0
            selected_type = 'jeepney'  # default
            
            for vtype, prob in dist.items():
                cumulative += prob
                if rand <= cumulative:
                    selected_type = vtype
                    break
            
            # Select random route
            route = random.choice(base_routes)
            
            xml_content += f'    <vehicle id="{selected_type}_{vehicle_id:04d}" type="{selected_type}" depart="{departure_time:.2f}">\n'
            xml_content += f'        <route edges="{route}" />\n'
            xml_content += f'    </vehicle>\n'
            
            vehicle_id += 1
    
    xml_content += '</routes>\n'
    
    # Write to file
    filename = 'KCCIntersection_busy_24hour.rou.xml'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"✅ Created busy traffic file: {filename}")
    print(f"✅ Total vehicles: {vehicle_id - 1}")
    print(f"✅ Average vehicles per hour: {(vehicle_id - 1) / 24:.1f}")
    
    return filename, vehicle_id - 1

def update_all_config_files(route_filename):
    """Update all configuration files to use the busy route file"""
    
    print(f"\n🔧 UPDATING CONFIGURATION FILES...")
    
    config_files = [
        'KCCIntersection.sumocfg',
        'KCCIntersection_24hour.sumocfg',
        'KCCIntersection_optimized.sumocfg',
        'KCCIntersection_baseline.sumocfg'
    ]
    
    for config_file in config_files:
        try:
            # Read current config
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update route file reference
            content = content.replace('KCCIntersection_24hour_realistic.rou.xml', route_filename)
            content = content.replace('KCCIntersection_24hour_continuous.rou.xml', route_filename)
            content = content.replace('KCCIntersection_500h.rou.xml', route_filename)
            content = content.replace('KCCIntersection.rou.xml', route_filename)
            
            # Write updated config
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Updated {config_file}")
            
        except Exception as e:
            print(f"   ⚠️  Could not update {config_file}: {e}")

def test_route_file(route_filename):
    """Test the route file to ensure it has vehicles"""
    
    print(f"\n🧪 TESTING ROUTE FILE...")
    
    try:
        tree = ET.parse(route_filename)
        root = tree.getroot()
        
        vehicles = root.findall('vehicle')
        if len(vehicles) == 0:
            print(f"   ❌ No vehicles found in {route_filename}")
            return False
        
        print(f"   ✅ Found {len(vehicles)} vehicles")
        
        # Check departure times
        departure_times = []
        for vehicle in vehicles[:10]:  # Check first 10
            depart_time = float(vehicle.get('depart'))
            departure_times.append(depart_time)
        
        print(f"   ✅ First few departure times: {departure_times}")
        
        # Check if early vehicles exist (within first hour)
        early_vehicles = [t for t in departure_times if t < 3600]
        print(f"   ✅ Vehicles in first hour: {len(early_vehicles)}")
        
        if len(early_vehicles) == 0:
            print(f"   ⚠️  No vehicles in first hour - simulation may appear empty initially")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing route file: {e}")
        return False

def main():
    """Main function to fix the no cars issue"""
    
    print("🚦 FIXING 'NO CARS' ISSUE IN SIMULATIONS")
    print("=" * 60)
    
    # Create busy traffic route file
    route_filename, total_vehicles = create_busy_traffic_route_file()
    
    # Update all configuration files
    update_all_config_files(route_filename)
    
    # Test the route file
    test_success = test_route_file(route_filename)
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Route file: {route_filename}")
    print(f"   ✅ Total vehicles: {total_vehicles}")
    print(f"   ✅ Vehicles per hour: {total_vehicles / 24:.1f}")
    print(f"   ✅ Configuration files updated")
    
    if test_success:
        print(f"\n🎯 READY TO TEST:")
        print(f"   1. Run: python optimized_traffic_controller.py")
        print(f"   2. Run: python baseline_traffic_controller.py")
        print(f"   3. Run: python run_comparison_study.py")
        print(f"\n✅ CARS SHOULD NOW BE VISIBLE IN BOTH SIMULATIONS!")
    else:
        print(f"\n❌ ROUTE FILE TEST FAILED - CHECK ROUTE FILE")

if __name__ == "__main__":
    main()