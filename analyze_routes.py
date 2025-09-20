#!/usr/bin/env python3
"""
Route Analysis Script for KCC Intersection Traffic Simulation
Identifies problematic routes that could cause vehicles to get stuck
"""

import xml.etree.ElementTree as ET

def analyze_routes():
    print("🔍 ANALYZING VEHICLE ROUTES FOR STUCK TRAFFIC ISSUES")
    print("=" * 60)
    
    try:
        # Parse the route file
        tree = ET.parse('KCCIntersection_realistic.rou.xml')
        root = tree.getroot()
        
        # Analyze routes
        short_routes = []
        incomplete_routes = []
        dead_end_routes = []
        total_vehicles = 0
        
        for vehicle in root.findall('vehicle'):
            route = vehicle.find('route')
            if route is not None:
                total_vehicles += 1
                edges = route.get('edges').split()
                vehicle_id = vehicle.get('id')
                edge_count = len(edges)
                
                # Check for very short routes (likely problematic)
                if edge_count <= 3:
                    short_routes.append((vehicle_id, edge_count, edges))
                
                # Check for routes ending with segment numbers (incomplete routes)
                last_edge = edges[-1] if edges else ''
                if (last_edge.endswith('#0') or last_edge.endswith('#1') or 
                    last_edge.endswith('#2') or last_edge.endswith('#3')):
                    incomplete_routes.append((vehicle_id, last_edge, edges))
                
                # Check for potential dead-end routes
                if edge_count == 1:
                    dead_end_routes.append((vehicle_id, edges[0]))
        
        print(f"📊 ROUTE ANALYSIS RESULTS:")
        print(f"Total vehicles: {total_vehicles}")
        print(f"Short routes (≤3 edges): {len(short_routes)}")
        print(f"Potentially incomplete routes: {len(incomplete_routes)}")
        print(f"Dead-end routes (1 edge): {len(dead_end_routes)}")
        
        print(f"\n🚨 SHORT ROUTES (likely to cause sticking):")
        for vid, count, edges in short_routes[:15]:
            print(f"  {vid}: {count} edges - {' '.join(edges)}")
        
        print(f"\n⚠️  INCOMPLETE ROUTES (ending mid-road):")
        for vid, last, edges in incomplete_routes[:15]:
            print(f"  {vid}: ends at {last}")
            
        print(f"\n🛑 DEAD-END ROUTES:")
        for vid, edge in dead_end_routes[:10]:
            print(f"  {vid}: single edge {edge}")
        
        # Calculate percentages
        short_pct = (len(short_routes) / total_vehicles) * 100
        incomplete_pct = (len(incomplete_routes) / total_vehicles) * 100
        dead_end_pct = (len(dead_end_routes) / total_vehicles) * 100
        
        print(f"\n📈 PROBLEM ROUTE PERCENTAGES:")
        print(f"Short routes: {short_pct:.1f}%")
        print(f"Incomplete routes: {incomplete_pct:.1f}%")
        print(f"Dead-end routes: {dead_end_pct:.1f}%")
        
        total_problematic = len(short_routes) + len(incomplete_routes) + len(dead_end_routes)
        total_problematic_pct = (total_problematic / total_vehicles) * 100
        
        print(f"\n🎯 SUMMARY:")
        print(f"Total problematic routes: {total_problematic}/{total_vehicles} ({total_problematic_pct:.1f}%)")
        
        if total_problematic_pct > 20:
            print("🚨 CRITICAL: High percentage of problematic routes!")
            print("   This explains why vehicles are getting stuck for hours.")
            print("   Recommendation: Create proper circular routes with exits.")
        elif total_problematic_pct > 10:
            print("⚠️  WARNING: Moderate number of problematic routes.")
            print("   Some vehicles may get stuck or cause congestion.")
        else:
            print("✅ Routes appear mostly healthy.")
            
    except Exception as e:
        print(f"Error analyzing routes: {e}")

if __name__ == "__main__":
    analyze_routes()