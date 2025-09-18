# =============================================================================
#           TRAFFIC METRICS ANALYSIS TOOL - ZAMBOANGA KCC
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class TrafficAnalyzer:
    def __init__(self, data_dir="."):
        """Initialize analyzer with data directory"""
        self.data_dir = data_dir
        self.metrics_df = None
        self.vehicle_df = None
        self.summary_df = None
        
    def load_data(self):
        """Load all CSV files"""
        try:
            print("Loading traffic metrics data...")
            
            # Load main metrics
            if os.path.exists(os.path.join(self.data_dir, 'traffic_metrics.csv')):
                self.metrics_df = pd.read_csv(os.path.join(self.data_dir, 'traffic_metrics.csv'))
                print(f"  ✓ Loaded {len(self.metrics_df)} traffic metric records")
            
            # Load vehicle details
            if os.path.exists(os.path.join(self.data_dir, 'vehicle_details.csv')):
                self.vehicle_df = pd.read_csv(os.path.join(self.data_dir, 'vehicle_details.csv'))
                print(f"  ✓ Loaded {len(self.vehicle_df)} vehicle journey records")
            
            # Load intersection summary
            if os.path.exists(os.path.join(self.data_dir, 'intersection_summary.csv')):
                self.summary_df = pd.read_csv(os.path.join(self.data_dir, 'intersection_summary.csv'))
                print(f"  ✓ Loaded {len(self.summary_df)} hourly summary records")
                
            print("Data loading complete!\n")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def generate_basic_statistics(self):
        """Generate basic statistical summary"""
        print("="*60)
        print("BASIC TRAFFIC STATISTICS")
        print("="*60)
        
        if self.metrics_df is not None:
            print("Overall Simulation Metrics:")
            print(f"  • Total simulation steps: {len(self.metrics_df):,}")
            print(f"  • Average vehicles in network: {self.metrics_df['Total_Vehicles'].mean():.1f}")
            print(f"  • Peak vehicle count: {self.metrics_df['Total_Vehicles'].max()}")
            print(f"  • Average network speed: {self.metrics_df['Average_Speed'].mean():.2f} m/s")
            print(f"  • Total CO2 emissions: {self.metrics_df['Total_CO2'].sum():.2f} mg")
            print(f"  • Total NOx emissions: {self.metrics_df['Total_NOx'].sum():.2f} mg")
            print(f"  • Total PMx emissions: {self.metrics_df['Total_PMx'].sum():.2f} mg")
        
        if self.vehicle_df is not None:
            print(f"\nVehicle Journey Statistics:")
            print(f"  • Total completed journeys: {len(self.vehicle_df):,}")
            print(f"  • Average travel time: {self.vehicle_df['Travel_Time'].mean():.1f} seconds")
            print(f"  • Average journey length: {self.vehicle_df['Route_Length'].mean():.1f} meters")
            print(f"  • Average journey speed: {self.vehicle_df['Average_Speed'].mean():.2f} m/s")
            print(f"  • Average waiting time: {self.vehicle_df['Total_Waiting_Time'].mean():.1f} seconds")
        
        if self.summary_df is not None:
            print(f"\nIntersection Performance:")
            j1_avg_delay = self.summary_df['J1_Avg_Delay'].mean()
            j2_avg_delay = self.summary_df['J2_Avg_Delay'].mean()
            j1_avg_queue = self.summary_df['J1_Avg_Queue'].mean()
            j2_avg_queue = self.summary_df['J2_Avg_Queue'].mean()
            
            print(f"  • J1 (Complex) - Avg delay: {j1_avg_delay:.1f}s, Avg queue: {j1_avg_queue:.1f}")
            print(f"  • J2 (4-way) - Avg delay: {j2_avg_delay:.1f}s, Avg queue: {j2_avg_queue:.1f}")
        
        print("="*60)
    
    def create_visualizations(self):
        """Create comprehensive visualizations"""
        print("Generating visualizations...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle('Traffic Control System Performance Analysis - 200 Hours', fontsize=16, fontweight='bold')
        
        if self.metrics_df is not None:
            # 1. Vehicle Count Over Time
            axes[0, 0].plot(self.metrics_df['Simulation_Step']/3600, self.metrics_df['Total_Vehicles'])
            axes[0, 0].set_title('Vehicle Count Over Time')
            axes[0, 0].set_xlabel('Time (Hours)')
            axes[0, 0].set_ylabel('Number of Vehicles')
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. Average Speed Over Time
            axes[0, 1].plot(self.metrics_df['Simulation_Step']/3600, self.metrics_df['Average_Speed'])
            axes[0, 1].set_title('Average Network Speed')
            axes[0, 1].set_xlabel('Time (Hours)')
            axes[0, 1].set_ylabel('Speed (m/s)')
            axes[0, 1].grid(True, alpha=0.3)
            
            # 3. Queue Lengths Comparison
            axes[1, 0].plot(self.metrics_df['Simulation_Step']/3600, self.metrics_df['J1_Queue_Length'], 
                           label='J1 (Complex)', alpha=0.7)
            axes[1, 0].plot(self.metrics_df['Simulation_Step']/3600, self.metrics_df['J2_Queue_Length'], 
                           label='J2 (4-way)', alpha=0.7)
            axes[1, 0].set_title('Queue Lengths at Intersections')
            axes[1, 0].set_xlabel('Time (Hours)')
            axes[1, 0].set_ylabel('Queue Length (vehicles)')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            
            # 4. Emissions Over Time
            axes[1, 1].plot(self.metrics_df['Simulation_Step']/3600, self.metrics_df['Total_CO2'].cumsum(), 
                           label='CO2', alpha=0.8)
            axes[1, 1].plot(self.metrics_df['Simulation_Step']/3600, self.metrics_df['Total_NOx'].cumsum(), 
                           label='NOx', alpha=0.8)
            axes[1, 1].set_title('Cumulative Emissions')
            axes[1, 1].set_xlabel('Time (Hours)')
            axes[1, 1].set_ylabel('Emissions (mg)')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        if self.vehicle_df is not None:
            # 5. Travel Time Distribution
            axes[2, 0].hist(self.vehicle_df['Travel_Time'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
            axes[2, 0].set_title('Travel Time Distribution')
            axes[2, 0].set_xlabel('Travel Time (seconds)')
            axes[2, 0].set_ylabel('Number of Vehicles')
            axes[2, 0].grid(True, alpha=0.3)
            
            # 6. Speed vs Travel Time Scatter
            sample_size = min(1000, len(self.vehicle_df))  # Sample for performance
            sample_df = self.vehicle_df.sample(n=sample_size)
            axes[2, 1].scatter(sample_df['Average_Speed'], sample_df['Travel_Time'], 
                              alpha=0.6, s=20, color='coral')
            axes[2, 1].set_title('Speed vs Travel Time Relationship')
            axes[2, 1].set_xlabel('Average Speed (m/s)')
            axes[2, 1].set_ylabel('Travel Time (seconds)')
            axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('traffic_analysis_dashboard.png', dpi=300, bbox_inches='tight')
        print("  ✓ Dashboard saved as 'traffic_analysis_dashboard.png'")
        
        # Create intersection comparison chart
        if self.summary_df is not None:
            fig2, axes2 = plt.subplots(2, 2, figsize=(12, 10))
            fig2.suptitle('Intersection Performance Comparison', fontsize=14, fontweight='bold')
            
            # Average Delay Comparison
            hours = self.summary_df['Hour']
            axes2[0, 0].plot(hours, self.summary_df['J1_Avg_Delay'], label='J1 (Complex)', linewidth=2)
            axes2[0, 0].plot(hours, self.summary_df['J2_Avg_Delay'], label='J2 (4-way)', linewidth=2)
            axes2[0, 0].set_title('Average Delay per Hour')
            axes2[0, 0].set_xlabel('Hour')
            axes2[0, 0].set_ylabel('Average Delay (seconds)')
            axes2[0, 0].legend()
            axes2[0, 0].grid(True, alpha=0.3)
            
            # Queue Length Comparison
            axes2[0, 1].plot(hours, self.summary_df['J1_Avg_Queue'], label='J1 (Complex)', linewidth=2)
            axes2[0, 1].plot(hours, self.summary_df['J2_Avg_Queue'], label='J2 (4-way)', linewidth=2)
            axes2[0, 1].set_title('Average Queue Length per Hour')
            axes2[0, 1].set_xlabel('Hour')
            axes2[0, 1].set_ylabel('Average Queue Length')
            axes2[0, 1].legend()
            axes2[0, 1].grid(True, alpha=0.3)
            
            # Phase Changes
            axes2[1, 0].bar(['J1 (Complex)', 'J2 (4-way)'], 
                           [self.summary_df['J1_Phase_Changes'].sum(), 
                            self.summary_df['J2_Phase_Changes'].sum()],
                           color=['lightblue', 'lightcoral'])
            axes2[1, 0].set_title('Total Phase Changes (200 hours)')
            axes2[1, 0].set_ylabel('Number of Phase Changes')
            
            # Vehicle Throughput
            axes2[1, 1].bar(['J1 (Complex)', 'J2 (4-way)'], 
                           [self.summary_df['J1_Total_Vehicles'].sum(), 
                            self.summary_df['J2_Total_Vehicles'].sum()],
                           color=['lightgreen', 'lightyellow'])
            axes2[1, 1].set_title('Total Vehicle Throughput (200 hours)')
            axes2[1, 1].set_ylabel('Number of Vehicles')
            
            plt.tight_layout()
            plt.savefig('intersection_comparison.png', dpi=300, bbox_inches='tight')
            print("  ✓ Intersection comparison saved as 'intersection_comparison.png'")
    
    def export_summary_report(self):
        """Export a comprehensive summary report"""
        print("Generating summary report...")
        
        with open('traffic_analysis_report.txt', 'w') as f:
            f.write("="*80 + "\n")
            f.write("SMART TRAFFIC CONTROL SYSTEM - PERFORMANCE ANALYSIS REPORT\n")
            f.write("Zamboanga KCC Intersection - 200 Hour Simulation\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-"*40 + "\n")
            
            if self.metrics_df is not None:
                avg_vehicles = self.metrics_df['Total_Vehicles'].mean()
                avg_speed = self.metrics_df['Average_Speed'].mean()
                total_co2 = self.metrics_df['Total_CO2'].sum()
                
                f.write(f"• Average vehicles in network: {avg_vehicles:.1f}\n")
                f.write(f"• Average network speed: {avg_speed:.2f} m/s ({avg_speed*3.6:.1f} km/h)\n")
                f.write(f"• Total CO2 emissions: {total_co2:.2f} mg\n")
            
            if self.vehicle_df is not None:
                avg_travel_time = self.vehicle_df['Travel_Time'].mean()
                avg_waiting = self.vehicle_df['Total_Waiting_Time'].mean()
                
                f.write(f"• Average travel time: {avg_travel_time:.1f} seconds ({avg_travel_time/60:.1f} minutes)\n")
                f.write(f"• Average waiting time: {avg_waiting:.1f} seconds\n")
                f.write(f"• Total completed journeys: {len(self.vehicle_df):,}\n")
            
            f.write("\n")
            
            # Detailed Analysis
            if self.summary_df is not None:
                f.write("INTERSECTION PERFORMANCE ANALYSIS\n")
                f.write("-"*40 + "\n")
                
                j1_delay = self.summary_df['J1_Avg_Delay'].mean()
                j2_delay = self.summary_df['J2_Avg_Delay'].mean()
                j1_queue = self.summary_df['J1_Avg_Queue'].mean()
                j2_queue = self.summary_df['J2_Avg_Queue'].mean()
                j1_changes = self.summary_df['J1_Phase_Changes'].sum()
                j2_changes = self.summary_df['J2_Phase_Changes'].sum()
                
                f.write(f"J1 (Complex Intersection):\n")
                f.write(f"  - Average delay: {j1_delay:.1f} seconds\n")
                f.write(f"  - Average queue length: {j1_queue:.1f} vehicles\n")
                f.write(f"  - Total phase changes: {j1_changes:,}\n")
                f.write(f"  - Total vehicles processed: {self.summary_df['J1_Total_Vehicles'].sum():,}\n\n")
                
                f.write(f"J2 (4-Way Intersection):\n")
                f.write(f"  - Average delay: {j2_delay:.1f} seconds\n")
                f.write(f"  - Average queue length: {j2_queue:.1f} vehicles\n")
                f.write(f"  - Total phase changes: {j2_changes:,}\n")
                f.write(f"  - Total vehicles processed: {self.summary_df['J2_Total_Vehicles'].sum():,}\n\n")
                
                # Performance comparison
                better_delay = "J1" if j1_delay < j2_delay else "J2"
                better_queue = "J1" if j1_queue < j2_queue else "J2"
                
                f.write(f"Performance Summary:\n")
                f.write(f"  - Lower average delay: {better_delay}\n")
                f.write(f"  - Lower average queue: {better_queue}\n")
                f.write(f"  - Delay difference: {abs(j1_delay - j2_delay):.1f} seconds\n")
                f.write(f"  - Queue difference: {abs(j1_queue - j2_queue):.1f} vehicles\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("Analysis complete. See generated visualizations for detailed insights.\n")
            f.write("Files generated:\n")
            f.write("  - traffic_analysis_dashboard.png\n")
            f.write("  - intersection_comparison.png\n")
            f.write("  - traffic_analysis_report.txt\n")
        
        print("  ✓ Summary report saved as 'traffic_analysis_report.txt'")
    
    def run_full_analysis(self):
        """Run complete analysis workflow"""
        print("Starting comprehensive traffic analysis...\n")
        
        if not self.load_data():
            print("Failed to load data. Please ensure CSV files exist.")
            return
        
        self.generate_basic_statistics()
        print("\n")
        self.create_visualizations()
        print("\n")
        self.export_summary_report()
        
        print(f"\n{'='*60}")
        print("ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        print("Check the generated files for detailed insights:")
        print("  📊 traffic_analysis_dashboard.png")
        print("  📈 intersection_comparison.png") 
        print("  📄 traffic_analysis_report.txt")
        print(f"{'='*60}")

# Run analysis if executed directly
if __name__ == "__main__":
    analyzer = TrafficAnalyzer()
    analyzer.run_full_analysis()
