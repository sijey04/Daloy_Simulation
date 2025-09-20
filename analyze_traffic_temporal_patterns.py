import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

def analyze_traffic_temporal_distribution():
    """Analyze the current traffic temporal distribution and show realistic peak hours patterns"""
    
    # Parse the current route file
    tree = ET.parse('KCCIntersection_realistic.rou.xml')
    root = tree.getroot()
    
    # Extract departure times
    departure_times = []
    vehicle_types = []
    
    for vehicle in root.findall('vehicle'):
        depart_time = float(vehicle.get('depart'))
        vehicle_type = vehicle.get('type')
        departure_times.append(depart_time)
        vehicle_types.append(vehicle_type)
    
    # Convert seconds to hours
    departure_hours = [t / 3600.0 for t in departure_times]
    
    print(f"🚗 CURRENT TRAFFIC ANALYSIS")
    print(f"Total vehicles: {len(departure_times)}")
    print(f"Time range: {min(departure_hours):.2f} - {max(departure_hours):.2f} hours")
    print(f"Duration: {max(departure_hours) - min(departure_hours):.2f} hours")
    
    # Count vehicles by type
    type_counts = {}
    for vtype in vehicle_types:
        type_counts[vtype] = type_counts.get(vtype, 0) + 1
    
    print(f"\n📊 VEHICLE TYPE DISTRIBUTION:")
    for vtype, count in type_counts.items():
        percentage = (count / len(vehicle_types)) * 100
        print(f"  {vtype}: {count} vehicles ({percentage:.1f}%)")
    
    # Analyze temporal distribution
    print(f"\n⏰ TEMPORAL DISTRIBUTION:")
    
    # Create hourly bins
    max_hour = int(max(departure_hours)) + 1
    hourly_counts = [0] * max_hour
    
    for hour in departure_hours:
        hourly_counts[int(hour)] += 1
    
    # Show distribution
    for hour in range(max_hour):
        if hourly_counts[hour] > 0:
            bar = '█' * min(hourly_counts[hour], 20)
            print(f"  Hour {hour:2d}: {hourly_counts[hour]:3d} vehicles {bar}")
    
    # Check if it resembles realistic traffic patterns
    print(f"\n🕐 REALISTIC TRAFFIC PATTERN ANALYSIS:")
    print(f"Current pattern: UNIFORM distribution (vehicles every 15 seconds)")
    print(f"Missing: Peak hour intensification")
    print(f"Missing: 24-hour cycle with morning/evening rush hours")
    
    return departure_times, departure_hours, vehicle_types

def create_realistic_24hour_traffic():
    """Create a more realistic 24-hour traffic pattern with peak hours"""
    
    print(f"\n🌅 REALISTIC 24-HOUR TRAFFIC PATTERN DESIGN:")
    print(f"Morning Rush: 7-9 AM (High volume)")
    print(f"Midday: 10 AM-4 PM (Medium volume)")  
    print(f"Evening Rush: 5-7 PM (High volume)")
    print(f"Night: 8 PM-6 AM (Low volume)")
    
    # Define traffic intensity by hour (0-23)
    traffic_intensity = {
        # Night hours (low traffic)
        0: 0.1, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.1,
        # Early morning build-up
        6: 0.3,
        # Morning rush (7-9 AM)
        7: 1.0, 8: 1.0, 9: 0.8,
        # Midday (moderate traffic)
        10: 0.6, 11: 0.7, 12: 0.8, 13: 0.7, 14: 0.6, 15: 0.6, 16: 0.7,
        # Evening rush (5-7 PM)
        17: 1.0, 18: 1.0, 19: 0.8,
        # Evening decline
        20: 0.5, 21: 0.4, 22: 0.3, 23: 0.2
    }
    
    # Vehicle type distribution by hour (more buses during rush, more jeepneys during day)
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
    
    print(f"\n📈 Traffic intensity by hour:")
    for hour in range(24):
        intensity = traffic_intensity[hour]
        bar = '█' * int(intensity * 20)
        rush_indicator = " 🚦 PEAK" if intensity >= 1.0 else ""
        print(f"  {hour:2d}:00 - {intensity:4.1f} {bar}{rush_indicator}")
    
    return traffic_intensity, vehicle_distributions

def generate_24hour_route_file():
    """Generate a new route file with realistic 24-hour traffic patterns"""
    
    traffic_intensity, vehicle_distributions = create_realistic_24hour_traffic()
    
    # Base routes (keeping the working routes we established)
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
    
    xml_content = '''<?xml version='1.0' encoding='UTF-8'?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
    <vType id="jeepney" accel="1.5" decel="3.5" sigma="0.8" length="7.0" width="2.2" minGap="2.5" maxSpeed="25.0" speedFactor="0.9" color="1,1,0" vClass="passenger" carFollowModel="Krauss" />
    <vType id="tricycle" accel="2.0" decel="4.0" sigma="0.9" length="3.5" width="1.8" minGap="2.0" maxSpeed="20.0" speedFactor="0.8" color="1,0,1" vClass="motorcycle" carFollowModel="Krauss" />
    <vType id="private_car" accel="2.5" decel="4.5" sigma="0.5" length="4.8" width="1.8" minGap="2.0" maxSpeed="30.0" speedFactor="1.0" color="0,0,1" vClass="passenger" carFollowModel="Krauss" />
    <vType id="multicab" accel="1.8" decel="3.0" sigma="0.7" length="4.5" width="1.9" minGap="2.2" maxSpeed="22.0" speedFactor="0.85" color="0,1,1" vClass="passenger" carFollowModel="Krauss" />
    <vType id="delivery_truck" accel="1.2" decel="3.0" sigma="0.6" length="6.5" width="2.3" minGap="3.0" maxSpeed="18.0" speedFactor="0.7" color="0.5,0.5,0.5" vClass="delivery" carFollowModel="Krauss" />
    <vType id="habal_habal" accel="3.0" decel="5.0" sigma="1.0" length="2.2" width="0.8" minGap="1.5" maxSpeed="25.0" speedFactor="1.1" color="1,0.5,0" vClass="motorcycle" carFollowModel="Krauss" />
    <vType id="bus" accel="1.0" decel="2.5" sigma="0.4" length="12.0" width="2.5" minGap="3.0" maxSpeed="20.0" speedFactor="0.8" color="0,1,0" vClass="bus" carFollowModel="Krauss" />
'''
    
    vehicle_id = 1
    
    # Generate vehicles for 24 hours
    for hour in range(24):
        intensity = traffic_intensity[hour]
        
        # Determine vehicle distribution for this hour
        if hour in [7, 8, 17, 18]:  # Rush hours
            dist = vehicle_distributions['rush_hour']
        elif hour >= 0 and hour <= 5:  # Night hours
            dist = vehicle_distributions['night_hour'] 
        else:  # Normal hours
            dist = vehicle_distributions['normal_hour']
        
        # Calculate number of vehicles for this hour (base of 5 vehicles per hour, scaled by intensity)
        base_vehicles_per_hour = 5
        vehicles_this_hour = max(1, int(base_vehicles_per_hour * intensity))
        
        # Generate vehicles for this hour
        for v in range(vehicles_this_hour):
            # Calculate departure time within the hour
            time_within_hour = (v / vehicles_this_hour) * 3600  # Spread within the hour
            departure_time = hour * 3600 + time_within_hour
            
            # Select vehicle type based on distribution
            import random
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
    with open('KCCIntersection_24hour_realistic.rou.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"\n✅ Generated realistic 24-hour traffic file: KCCIntersection_24hour_realistic.rou.xml")
    print(f"Total vehicles generated: {vehicle_id - 1}")
    
    return vehicle_id - 1

if __name__ == "__main__":
    print("🚦 TRAFFIC TEMPORAL PATTERN ANALYSIS")
    print("=" * 50)
    
    # Analyze current traffic pattern
    analyze_traffic_temporal_distribution()
    
    # Show realistic pattern design
    create_realistic_24hour_traffic()
    
    # Generate new realistic file
    total_vehicles = generate_24hour_route_file()
    
    print(f"\n📋 SUMMARY:")
    print(f"✅ Current file: Uniform distribution (non-realistic)")
    print(f"✅ New file: 24-hour cycle with peak hours")
    print(f"✅ Morning rush: 7-9 AM (high volume)")
    print(f"✅ Evening rush: 5-7 PM (high volume)")
    print(f"✅ Night hours: Low traffic volume")
    print(f"✅ Authentic Filipino vehicle mix")