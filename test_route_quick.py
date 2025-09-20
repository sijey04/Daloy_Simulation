import xml.etree.ElementTree as ET
import os

def test_route_file():
    """Test the route file to see if it has vehicles"""
    
    route_file = "KCCIntersection_24hour_continuous.rou.xml"
    
    if not os.path.exists(route_file):
        print(f"❌ ERROR: Route file {route_file} not found!")
        return False
    
    try:
        # Parse the route file
        tree = ET.parse(route_file)
        root = tree.getroot()
        
        # Count vehicles
        vehicles = root.findall('vehicle')
        print(f"✅ Route file found: {route_file}")
        print(f"📊 Total vehicles in route file: {len(vehicles)}")
        
        if len(vehicles) == 0:
            print("❌ NO VEHICLES FOUND! This is why the simulation is empty.")
            return False
        
        # Check first few vehicles
        print(f"\n🚗 First 5 vehicles:")
        for i, vehicle in enumerate(vehicles[:5]):
            veh_id = vehicle.get('id')
            veh_type = vehicle.get('type')
            depart_time = vehicle.get('depart')
            print(f"   {i+1}. {veh_id} ({veh_type}) - departs at {depart_time}s")
        
        # Check departure times
        departure_times = []
        for vehicle in vehicles:
            depart_time = float(vehicle.get('depart'))
            departure_times.append(depart_time)
        
        departure_times.sort()
        print(f"\n⏰ Departure time analysis:")
        print(f"   First vehicle: {departure_times[0]} seconds")
        print(f"   Last vehicle: {departure_times[-1]} seconds")
        print(f"   Time span: {departure_times[-1] - departure_times[0]:.0f} seconds ({(departure_times[-1] - departure_times[0])/3600:.1f} hours)")
        
        # Check for early vehicles (first 10 minutes)
        early_vehicles = [t for t in departure_times if t <= 600]
        print(f"   Vehicles in first 10 minutes: {len(early_vehicles)}")
        
        if len(early_vehicles) == 0:
            print("⚠️  WARNING: No vehicles in first 10 minutes - simulation will appear empty initially!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading route file: {e}")
        return False

if __name__ == "__main__":
    test_route_file()