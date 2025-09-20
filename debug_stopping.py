#!/usr/bin/env python3
"""
Debug Simulation Stopping Issue
"""

import os
import sys
import xml.etree.ElementTree as ET

# Add SUMO tools to path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

def debug_simulation_stopping():
    print("🔍 DEBUGGING SIMULATION STOPPING ISSUE")
    print("=" * 60)
    
    # 1. Check route file validity
    print("1. CHECKING ROUTE FILE:")
    try:
        tree = ET.parse('KCCIntersection_super_visible.rou.xml')
        root = tree.getroot()
        vehicles = root.findall('vehicle')
        print(f"   ✅ Route file valid: {len(vehicles)} vehicles")
        
        # Check first few vehicles
        for i, v in enumerate(vehicles[:5]):
            depart = v.get('depart')
            route_elem = v.find('route')
            edges = route_elem.get('edges') if route_elem is not None else 'NO ROUTE'
            print(f"   Vehicle {i+1}: depart={depart}s, route={edges[:50]}...")
            
    except Exception as e:
        print(f"   ❌ Route file error: {e}")
        return
    
    # 2. Check network compatibility
    print("\n2. CHECKING NETWORK COMPATIBILITY:")
    try:
        net_tree = ET.parse('KCCIntersection.net.xml')
        net_root = net_tree.getroot()
        edges = [edge.get('id') for edge in net_root.findall('edge')]
        print(f"   ✅ Network file valid: {len(edges)} edges")
        
        # Check if route edges exist in network
        route_tree = ET.parse('KCCIntersection_super_visible.rou.xml')
        route_root = route_tree.getroot()
        first_vehicle = route_root.find('vehicle')
        if first_vehicle:
            route_elem = first_vehicle.find('route')
            if route_elem:
                route_edges = route_elem.get('edges').split()
                missing = [e for e in route_edges if e not in edges]
                if missing:
                    print(f"   ❌ Missing edges: {missing}")
                else:
                    print(f"   ✅ All route edges exist in network")
                    
    except Exception as e:
        print(f"   ❌ Network check error: {e}")
        return
    
    # 3. Test simulation start
    print("\n3. TESTING SIMULATION START:")
    try:
        # Close any existing connections
        try:
            traci.close()
        except:
            pass
            
        # Start SUMO with detailed logging
        print("   Starting SUMO...")
        traci.start(["sumo-gui", "-c", "KCCIntersection_optimized.sumocfg", 
                    "--start", "--quit-on-end", "--verbose"])
        
        print("   ✅ SUMO started successfully")
        
        # Test first few steps
        vehicles_seen = set()
        for step in range(10):
            try:
                traci.simulationStep()
                current_vehicles = traci.vehicle.getIDList()
                vehicles_seen.update(current_vehicles)
                
                # Check simulation state
                min_expected = traci.simulation.getMinExpectedNumber()
                loaded_vehicles = traci.simulation.getLoadedNumber()
                
                print(f"   Step {step}: Active={len(current_vehicles)}, Expected={min_expected}, Loaded={loaded_vehicles}")
                
                if len(current_vehicles) == 0 and min_expected == 0 and step > 2:
                    print(f"   ⚠️  No vehicles expected after step {step}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Simulation step {step} failed: {e}")
                break
        
        print(f"   Total vehicles seen: {len(vehicles_seen)}")
        if vehicles_seen:
            print(f"   Vehicle IDs: {list(vehicles_seen)}")
        
        traci.close()
        
    except Exception as e:
        print(f"   ❌ Simulation test failed: {e}")
        try:
            traci.close()
        except:
            pass
    
    # 4. Create fixed configuration
    print("\n4. CREATING FIXED CONFIGURATION:")
    create_fixed_config()

def create_fixed_config():
    """Create a fixed configuration that won't stop early"""
    
    # Read current config
    try:
        with open('KCCIntersection_optimized.sumocfg', 'r') as f:
            content = f.read()
        
        # Create fixed config content
        fixed_config = '''<configuration>
    <input>
        <net-file value="KCCIntersection.net.xml"/>
        <route-files value="KCCIntersection_super_visible.rou.xml"/>
        <additional-files value="KCCIntersectionConfig.add.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="86400"/>
        <step-length value="1"/>
    </time>
    <processing>
        <ignore-junction-blocker value="5"/>
        <time-to-teleport value="-1"/>
        <time-to-impatience value="300"/>
        <max-depart-delay value="-1"/>
        <ignore-route-errors value="true"/>
    </processing>
    <output>
        <tripinfo-output value="optimized_tripinfo.xml"/>
        <summary-output value="optimized_summary.xml"/>
    </output>
    <gui>
        <gui-settings-file value="gui-settings.xml"/>
        <start value="true"/>
        <quit-on-end value="false"/>
    </gui>
    <report>
        <no-warnings value="true"/>
        <duration-log.disable value="true"/>
        <no-step-log value="true"/>
        <verbose value="false"/>
    </report>
</configuration>'''
        
        # Save fixed config
        with open('KCCIntersection_optimized_fixed.sumocfg', 'w') as f:
            f.write(fixed_config)
        
        print("   ✅ Created fixed config: KCCIntersection_optimized_fixed.sumocfg")
        
        # Also create simple baseline config
        baseline_config = '''<configuration>
    <input>
        <net-file value="KCCIntersection.net.xml"/>
        <route-files value="KCCIntersection_super_visible.rou.xml"/>
        <additional-files value="KCCIntersectionConfig.add.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="86400"/>
        <step-length value="1"/>
    </time>
    <processing>
        <ignore-junction-blocker value="5"/>
        <time-to-teleport value="-1"/>
        <time-to-impatience value="300"/>
        <max-depart-delay value="-1"/>
        <ignore-route-errors value="true"/>
    </processing>
    <output>
        <tripinfo-output value="baseline_tripinfo.xml"/>
        <summary-output value="baseline_summary.xml"/>
    </output>
    <gui>
        <gui-settings-file value="gui-settings.xml"/>
        <start value="true"/>
        <quit-on-end value="false"/>
    </gui>
    <report>
        <no-warnings value="true"/>
        <duration-log.disable value="true"/>
        <no-step-log value="true"/>
        <verbose value="false"/>
    </report>
</configuration>'''
        
        with open('KCCIntersection_baseline_fixed.sumocfg', 'w') as f:
            f.write(baseline_config)
        
        print("   ✅ Created fixed baseline config: KCCIntersection_baseline_fixed.sumocfg")
        
    except Exception as e:
        print(f"   ❌ Error creating fixed config: {e}")

if __name__ == "__main__":
    debug_simulation_stopping()