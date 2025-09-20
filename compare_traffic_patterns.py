import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

def compare_traffic_patterns():
    """Compare current uniform pattern vs realistic 24-hour pattern"""
    
    # Parse current route file
    tree_current = ET.parse('KCCIntersection_realistic.rou.xml')
    root_current = tree_current.getroot()
    
    # Parse new 24-hour file
    tree_24h = ET.parse('KCCIntersection_24hour_realistic.rou.xml')
    root_24h = tree_24h.getroot()
    
    # Extract departure times
    current_times = []
    current_types = []
    
    for vehicle in root_current.findall('vehicle'):
        depart_time = float(vehicle.get('depart'))
        vehicle_type = vehicle.get('type')
        current_times.append(depart_time / 3600.0)  # Convert to hours
        current_types.append(vehicle_type)
    
    # Extract 24-hour departure times
    realistic_times = []
    realistic_types = []
    
    for vehicle in root_24h.findall('vehicle'):
        depart_time = float(vehicle.get('depart'))
        vehicle_type = vehicle.get('type')
        realistic_times.append(depart_time / 3600.0)  # Convert to hours
        realistic_types.append(vehicle_type)
    
    # Create comparison visualization
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Traffic Pattern Comparison: Current vs Realistic 24-Hour', fontsize=16, fontweight='bold')
    
    # Plot 1: Current pattern histogram
    ax1.hist(current_times, bins=20, alpha=0.7, color='red', edgecolor='black')
    ax1.set_title('CURRENT: Uniform Distribution (0.5 hours)', fontweight='bold')
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Number of Vehicles')
    ax1.grid(True, alpha=0.3)
    ax1.text(0.02, 0.95, f'Total: {len(current_times)} vehicles\nDuration: {max(current_times):.1f} hours', 
             transform=ax1.transAxes, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Plot 2: 24-hour pattern histogram
    ax2.hist(realistic_times, bins=24, alpha=0.7, color='green', edgecolor='black')
    ax2.set_title('REALISTIC: 24-Hour with Peak Hours', fontweight='bold')
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('Number of Vehicles')
    ax2.grid(True, alpha=0.3)
    
    # Add peak hour annotations
    ax2.axvspan(7, 9, alpha=0.2, color='orange', label='Morning Rush')
    ax2.axvspan(17, 19, alpha=0.2, color='orange', label='Evening Rush')
    ax2.legend()
    ax2.text(0.02, 0.95, f'Total: {len(realistic_times)} vehicles\nDuration: {max(realistic_times):.1f} hours', 
             transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # Plot 3: Current vehicle type distribution
    current_type_counts = {}
    for vtype in current_types:
        current_type_counts[vtype] = current_type_counts.get(vtype, 0) + 1
    
    ax3.pie(current_type_counts.values(), labels=current_type_counts.keys(), autopct='%1.1f%%')
    ax3.set_title('CURRENT: Vehicle Type Distribution', fontweight='bold')
    
    # Plot 4: 24-hour vehicle type distribution
    realistic_type_counts = {}
    for vtype in realistic_types:
        realistic_type_counts[vtype] = realistic_type_counts.get(vtype, 0) + 1
    
    ax4.pie(realistic_type_counts.values(), labels=realistic_type_counts.keys(), autopct='%1.1f%%')
    ax4.set_title('REALISTIC: Vehicle Type Distribution', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('traffic_pattern_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Comparison visualization saved as 'traffic_pattern_comparison.png'")
    
    # Create detailed hourly analysis
    fig2, (ax5, ax6) = plt.subplots(2, 1, figsize=(16, 10))
    fig2.suptitle('Detailed 24-Hour Traffic Analysis', fontsize=16, fontweight='bold')
    
    # Hourly distribution for realistic pattern
    hourly_counts = [0] * 24
    for hour_time in realistic_times:
        hour_int = int(hour_time) % 24
        hourly_counts[hour_int] += 1
    
    hours = list(range(24))
    colors = ['red' if h in [7, 8, 17, 18] else 'blue' if h in [9, 10, 11, 12, 13, 14, 15, 16, 19] else 'gray' for h in hours]
    
    bars = ax5.bar(hours, hourly_counts, color=colors, alpha=0.7, edgecolor='black')
    ax5.set_title('Realistic 24-Hour Traffic Volume by Hour', fontweight='bold')
    ax5.set_xlabel('Hour of Day')
    ax5.set_ylabel('Number of Vehicles')
    ax5.set_xticks(range(0, 24, 2))
    ax5.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
    ax5.grid(True, alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='red', alpha=0.7, label='Peak Hours (7-9 AM, 5-7 PM)'),
                      Patch(facecolor='blue', alpha=0.7, label='Normal Hours'),
                      Patch(facecolor='gray', alpha=0.7, label='Night Hours')]
    ax5.legend(handles=legend_elements)
    
    # Traffic intensity comparison
    intensity_pattern = {
        0: 0.1, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.1, 6: 0.3,
        7: 1.0, 8: 1.0, 9: 0.8, 10: 0.6, 11: 0.7, 12: 0.8,
        13: 0.7, 14: 0.6, 15: 0.6, 16: 0.7, 17: 1.0, 18: 1.0,
        19: 0.8, 20: 0.5, 21: 0.4, 22: 0.3, 23: 0.2
    }
    
    intensities = [intensity_pattern[h] for h in range(24)]
    ax6.plot(hours, intensities, 'o-', linewidth=3, markersize=8, color='orange')
    ax6.fill_between(hours, intensities, alpha=0.3, color='orange')
    ax6.set_title('Designed Traffic Intensity Pattern', fontweight='bold')
    ax6.set_xlabel('Hour of Day')
    ax6.set_ylabel('Traffic Intensity (Relative)')
    ax6.set_xticks(range(0, 24, 2))
    ax6.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
    ax6.grid(True, alpha=0.3)
    ax6.axhspan(0.8, 1.0, alpha=0.2, color='red', label='Peak Intensity')
    ax6.legend()
    
    plt.tight_layout()
    plt.savefig('traffic_hourly_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Hourly analysis saved as 'traffic_hourly_analysis.png'")
    
    # Print comparison summary
    print("\n" + "="*80)
    print("TRAFFIC PATTERN COMPARISON SUMMARY")
    print("="*80)
    print(f"CURRENT SIMULATION:")
    print(f"  • Pattern: Uniform distribution")
    print(f"  • Duration: {max(current_times):.1f} hours")
    print(f"  • Total vehicles: {len(current_times)}")
    print(f"  • Average interval: {(max(current_times)*3600/len(current_times)):.1f} seconds")
    print(f"  • Peak hours: NONE")
    
    print(f"\nREALISITC 24-HOUR SIMULATION:")
    print(f"  • Pattern: Realistic daily cycle")
    print(f"  • Duration: {max(realistic_times):.1f} hours") 
    print(f"  • Total vehicles: {len(realistic_times)}")
    print(f"  • Morning rush: 7-9 AM (High volume)")
    print(f"  • Evening rush: 5-7 PM (High volume)")
    print(f"  • Night hours: Low traffic volume")
    
    print(f"\nRECOMMENDATION:")
    print(f"  ✅ Use 'KCCIntersection_24hour_realistic.rou.xml' for realistic simulation")
    print(f"  ✅ Update your SUMO configuration to use the new route file")
    print(f"  ✅ This will properly replicate peak hour intensification")
    print("="*80)

if __name__ == "__main__":
    compare_traffic_patterns()