# =============================================================================
#           TRAFFIC METRICS ANALYSIS TOOL - ZAMBOANGA KCC
#           UPDATED FOR OPTIMIZED 500-HOUR CONTROLLER INTEGRATION
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class OptimizedTrafficAnalyzer:
    def __init__(self, data_dir="."):
        """Initialize analyzer with data directory for optimized controller"""
        self.data_dir = data_dir
        self.metrics_df = None
        self.simulation_hours = 0
        self.is_500h_simulation = False
        
    def load_data(self):
        """Load optimized controller CSV data"""
        try:
            print("Loading optimized traffic controller data...")
            
            # Try to load 500-hour data first
            if os.path.exists(os.path.join(self.data_dir, 'traffic_metrics_500h.csv')):
                self.metrics_df = pd.read_csv(os.path.join(self.data_dir, 'traffic_metrics_500h.csv'))
                if len(self.metrics_df) > 0:
                    self.is_500h_simulation = True
                    self.simulation_hours = 500
                    print(f"  ✓ Loaded 500-hour simulation data: {len(self.metrics_df):,} records")
                else:
                    print("  ⚠️ 500-hour file exists but is empty, trying other files...")
                    self.metrics_df = None
            
            # Fallback to standard optimized data
            if self.metrics_df is None and os.path.exists(os.path.join(self.data_dir, 'optimized_traffic_metrics.csv')):
                self.metrics_df = pd.read_csv(os.path.join(self.data_dir, 'optimized_traffic_metrics.csv'))
                self.simulation_hours = len(self.metrics_df) // 360  # Estimate based on steps
                print(f"  ✓ Loaded optimized traffic data: {len(self.metrics_df):,} records")
            
            # Legacy format support
            if self.metrics_df is None and os.path.exists(os.path.join(self.data_dir, 'traffic_metrics.csv')):
                self.metrics_df = pd.read_csv(os.path.join(self.data_dir, 'traffic_metrics.csv'))
                self.simulation_hours = len(self.metrics_df) // 360  # Estimate
                print(f"  ✓ Loaded legacy traffic data: {len(self.metrics_df):,} records")
            
            if self.metrics_df is None:
                print("  ❌ No compatible traffic metrics file found!")
                print("     Expected: traffic_metrics_500h.csv, optimized_traffic_metrics.csv, or traffic_metrics.csv")
                return False
            
            # Ensure required columns exist or create them
            self.validate_and_enhance_data()
            
            print("Data loading complete!\n")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def validate_and_enhance_data(self):
        """Validate and enhance the loaded data"""
        if self.metrics_df is None or len(self.metrics_df) == 0:
            print("  ⚠️ No data found in metrics file")
            return
        
        # Check for required columns and add missing ones
        required_columns = ['Step', 'Time', 'Vehicles', 'J1_Phase', 'J2_Phase', 
                          'J1_Queue', 'J2_Queue', 'J1_Waiting', 'J2_Waiting']
        
        for col in required_columns:
            if col not in self.metrics_df.columns:
                print(f"  ⚠️ Missing column '{col}', adding with default values")
                self.metrics_df[col] = 0
        
        # Add derived columns for analysis
        if 'Hour' not in self.metrics_df.columns:
            self.metrics_df['Hour'] = self.metrics_df['Step'] // 3600
        
        if 'Total_Queue' not in self.metrics_df.columns:
            self.metrics_df['Total_Queue'] = self.metrics_df['J1_Queue'] + self.metrics_df['J2_Queue']
        
        if 'Average_Waiting' not in self.metrics_df.columns:
            self.metrics_df['Average_Waiting'] = (self.metrics_df['J1_Waiting'] + self.metrics_df['J2_Waiting']) / 2
    
    def generate_basic_statistics(self):
        """Generate basic statistical summary for optimized controller"""
        print("="*70)
        print("OPTIMIZED TRAFFIC CONTROL SYSTEM - STATISTICAL ANALYSIS")
        print("="*70)
        
        if self.metrics_df is not None:
            duration_text = f"{self.simulation_hours}-HOUR" if self.simulation_hours > 0 else "EXTENDED"
            print(f"📊 {duration_text} SIMULATION PERFORMANCE:")
            print(f"  • Total simulation steps: {len(self.metrics_df):,}")
            print(f"  • Simulation duration: {self.simulation_hours} hours" if self.simulation_hours > 0 else "")
            print(f"  • Data points collected: {len(self.metrics_df):,}")
            
            # Basic traffic metrics
            print(f"\n🚗 TRAFFIC FLOW METRICS:")
            print(f"  • Average vehicles in network: {self.metrics_df['Vehicles'].mean():.1f}")
            print(f"  • Peak vehicle count: {self.metrics_df['Vehicles'].max()}")
            print(f"  • Minimum vehicle count: {self.metrics_df['Vehicles'].min()}")
            print(f"  • Vehicle count std deviation: {self.metrics_df['Vehicles'].std():.1f}")
            
            # Queue analysis
            print(f"\n🚦 INTERSECTION QUEUE ANALYSIS:")
            print(f"  • J1 Average queue length: {self.metrics_df['J1_Queue'].mean():.2f} vehicles")
            print(f"  • J2 Average queue length: {self.metrics_df['J2_Queue'].mean():.2f} vehicles")
            print(f"  • J1 Maximum queue length: {self.metrics_df['J1_Queue'].max()} vehicles")
            print(f"  • J2 Maximum queue length: {self.metrics_df['J2_Queue'].max()} vehicles")
            print(f"  • Total network average queue: {self.metrics_df['Total_Queue'].mean():.2f} vehicles")
            
            # Waiting time analysis
            print(f"\n⏱️ WAITING TIME ANALYSIS:")
            print(f"  • J1 Average waiting time: {self.metrics_df['J1_Waiting'].mean():.2f} seconds")
            print(f"  • J2 Average waiting time: {self.metrics_df['J2_Waiting'].mean():.2f} seconds")
            print(f"  • Network average waiting time: {self.metrics_df['Average_Waiting'].mean():.2f} seconds")
            
            # Phase change analysis
            phase_changes = self.analyze_phase_changes()
            print(f"\n🔄 TRAFFIC LIGHT PERFORMANCE:")
            print(f"  • J1 Total phase changes: {phase_changes['J1']:,}")
            print(f"  • J2 Total phase changes: {phase_changes['J2']:,}")
            print(f"  • J1 Average time between changes: {phase_changes['J1_avg_time']:.1f} seconds")
            print(f"  • J2 Average time between changes: {phase_changes['J2_avg_time']:.1f} seconds")
            
            # Performance summary
            efficiency_score = self.calculate_efficiency_score()
            print(f"\n⭐ SYSTEM EFFICIENCY:")
            print(f"  • Overall efficiency score: {efficiency_score:.2f}/10")
            print(f"  • Queue management rating: {self.rate_queue_management()}")
            print(f"  • Traffic flow rating: {self.rate_traffic_flow()}")
        
        print("="*70)
    
    def analyze_phase_changes(self):
        """Analyze traffic light phase change patterns"""
        if self.metrics_df is None:
            return {'J1': 0, 'J2': 0, 'J1_avg_time': 0, 'J2_avg_time': 0}
        
        # Count phase changes by detecting when phase values change
        j1_changes = (self.metrics_df['J1_Phase'].diff() != 0).sum()
        j2_changes = (self.metrics_df['J2_Phase'].diff() != 0).sum()
        
        # Calculate average time between changes
        total_time = len(self.metrics_df) * 10  # Assuming 10-second intervals
        j1_avg_time = total_time / max(1, j1_changes)
        j2_avg_time = total_time / max(1, j2_changes)
        
        return {
            'J1': j1_changes,
            'J2': j2_changes,
            'J1_avg_time': j1_avg_time,
            'J2_avg_time': j2_avg_time
        }
    
    def calculate_efficiency_score(self):
        """Calculate overall system efficiency score (0-10)"""
        if self.metrics_df is None:
            return 0
        
        # Normalize metrics for scoring
        avg_queue = self.metrics_df['Total_Queue'].mean()
        avg_waiting = self.metrics_df['Average_Waiting'].mean()
        vehicle_variance = self.metrics_df['Vehicles'].std()
        
        # Score components (lower is better for queue/waiting, higher for stability)
        queue_score = max(0, 10 - (avg_queue / 5))  # Penalty for long queues
        waiting_score = max(0, 10 - (avg_waiting / 10))  # Penalty for long waits
        stability_score = max(0, 10 - (vehicle_variance / 10))  # Bonus for stability
        
        return (queue_score + waiting_score + stability_score) / 3
    
    def rate_queue_management(self):
        """Rate queue management performance"""
        if self.metrics_df is None:
            return "Unknown"
        
        avg_queue = self.metrics_df['Total_Queue'].mean()
        max_queue = self.metrics_df['Total_Queue'].max()
        
        if avg_queue < 5 and max_queue < 15:
            return "Excellent"
        elif avg_queue < 10 and max_queue < 25:
            return "Good"
        elif avg_queue < 15 and max_queue < 35:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def rate_traffic_flow(self):
        """Rate traffic flow performance"""
        if self.metrics_df is None:
            return "Unknown"
        
        avg_waiting = self.metrics_df['Average_Waiting'].mean()
        
        if avg_waiting < 5:
            return "Excellent"
        elif avg_waiting < 10:
            return "Good"
        elif avg_waiting < 20:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def create_visualizations(self):
        """Create comprehensive visualizations for optimized controller"""
        print("Generating optimized traffic analysis visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        duration_text = f"{self.simulation_hours}H" if self.simulation_hours > 0 else "Extended"
        fig, axes = plt.subplots(3, 2, figsize=(16, 20))
        fig.suptitle(f'Optimized Traffic Control System - {duration_text} Analysis', fontsize=16, fontweight='bold')
        
        if self.metrics_df is not None and len(self.metrics_df) > 0:
            # 1. Vehicle Count Over Time
            time_hours = self.metrics_df['Step'] / 3600
            axes[0, 0].plot(time_hours, self.metrics_df['Vehicles'], alpha=0.7, linewidth=1)
            axes[0, 0].set_title('Vehicle Count Over Time', fontweight='bold')
            axes[0, 0].set_xlabel('Time (Hours)')
            axes[0, 0].set_ylabel('Number of Vehicles')
            axes[0, 0].grid(True, alpha=0.3)
            if len(time_hours) > 0:
                axes[0, 0].set_xlim(0, max(time_hours))
            
            # 2. Queue Lengths Comparison
            axes[0, 1].plot(time_hours, self.metrics_df['J1_Queue'], 
                           label='J1 (Complex)', alpha=0.8, linewidth=1, color='red')
            axes[0, 1].plot(time_hours, self.metrics_df['J2_Queue'], 
                           label='J2 (4-way)', alpha=0.8, linewidth=1, color='blue')
            axes[0, 1].plot(time_hours, self.metrics_df['Total_Queue'], 
                           label='Total Network', alpha=0.6, linewidth=1, color='green')
            axes[0, 1].set_title('Queue Lengths at Intersections', fontweight='bold')
            axes[0, 1].set_xlabel('Time (Hours)')
            axes[0, 1].set_ylabel('Queue Length (vehicles)')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].set_xlim(0, max(time_hours) if len(time_hours) > 0 else 1)
            
            # 3. Waiting Times Comparison
            axes[1, 0].plot(time_hours, self.metrics_df['J1_Waiting'], 
                           label='J1 (Complex)', alpha=0.8, linewidth=1, color='orange')
            axes[1, 0].plot(time_hours, self.metrics_df['J2_Waiting'], 
                           label='J2 (4-way)', alpha=0.8, linewidth=1, color='purple')
            axes[1, 0].plot(time_hours, self.metrics_df['Average_Waiting'], 
                           label='Network Average', alpha=0.6, linewidth=1, color='brown')
            axes[1, 0].set_title('Waiting Times at Intersections', fontweight='bold')
            axes[1, 0].set_xlabel('Time (Hours)')
            axes[1, 0].set_ylabel('Waiting Time (seconds)')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].set_xlim(0, max(time_hours) if len(time_hours) > 0 else 1)
            
            # 4. Phase Change Activity
            j1_phase_diff = (self.metrics_df['J1_Phase'].diff() != 0).astype(int)
            j2_phase_diff = (self.metrics_df['J2_Phase'].diff() != 0).astype(int)
            
            # Rolling sum for phase changes per hour
            window_size = 360  # 1 hour worth of data points
            j1_hourly_changes = j1_phase_diff.rolling(window=window_size, min_periods=1).sum()
            j2_hourly_changes = j2_phase_diff.rolling(window=window_size, min_periods=1).sum()
            
            axes[1, 1].plot(time_hours, j1_hourly_changes, 
                           label='J1 Phase Changes/Hour', alpha=0.8, linewidth=1, color='red')
            axes[1, 1].plot(time_hours, j2_hourly_changes, 
                           label='J2 Phase Changes/Hour', alpha=0.8, linewidth=1, color='blue')
            axes[1, 1].set_title('Traffic Light Activity (Changes per Hour)', fontweight='bold')
            axes[1, 1].set_xlabel('Time (Hours)')
            axes[1, 1].set_ylabel('Phase Changes per Hour')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].set_xlim(0, max(time_hours) if len(time_hours) > 0 else 1)
            
            # 5. Performance Distribution - Queue Length
            axes[2, 0].hist(self.metrics_df['J1_Queue'], bins=30, alpha=0.6, 
                           color='red', label='J1 Queue', density=True)
            axes[2, 0].hist(self.metrics_df['J2_Queue'], bins=30, alpha=0.6, 
                           color='blue', label='J2 Queue', density=True)
            axes[2, 0].set_title('Queue Length Distribution', fontweight='bold')
            axes[2, 0].set_xlabel('Queue Length (vehicles)')
            axes[2, 0].set_ylabel('Probability Density')
            axes[2, 0].legend()
            axes[2, 0].grid(True, alpha=0.3)
            
            # 6. System Performance Heatmap (Hourly Averages)
            if len(self.metrics_df) > 3600:  # Only if we have at least 1 hour of data
                hourly_data = self.metrics_df.groupby('Hour').agg({
                    'J1_Queue': 'mean',
                    'J2_Queue': 'mean',
                    'J1_Waiting': 'mean',
                    'J2_Waiting': 'mean'
                }).reset_index()
                
                if len(hourly_data) > 1:
                    # Create heatmap data
                    heatmap_data = hourly_data[['J1_Queue', 'J2_Queue', 'J1_Waiting', 'J2_Waiting']].T
                    im = axes[2, 1].imshow(heatmap_data.values, cmap='YlOrRd', aspect='auto')
                    axes[2, 1].set_title('Performance Heatmap (Hourly Averages)', fontweight='bold')
                    axes[2, 1].set_xlabel('Hour')
                    axes[2, 1].set_ylabel('Metrics')
                    axes[2, 1].set_yticks(range(len(heatmap_data)))
                    axes[2, 1].set_yticklabels(['J1 Queue', 'J2 Queue', 'J1 Wait', 'J2 Wait'])
                    
                    # Add colorbar
                    cbar = plt.colorbar(im, ax=axes[2, 1])
                    cbar.set_label('Average Value')
                else:
                    axes[2, 1].text(0.5, 0.5, 'Insufficient data\nfor heatmap', 
                                   ha='center', va='center', transform=axes[2, 1].transAxes)
                    axes[2, 1].set_title('Performance Heatmap (Not Available)', fontweight='bold')
            else:
                axes[2, 1].text(0.5, 0.5, 'Insufficient data\nfor heatmap', 
                               ha='center', va='center', transform=axes[2, 1].transAxes)
                axes[2, 1].set_title('Performance Heatmap (Not Available)', fontweight='bold')
        
        plt.tight_layout()
        filename = f'optimized_traffic_analysis_{duration_text.lower()}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  ✓ Dashboard saved as '{filename}'")
        
        # Create intersection comparison chart
        self.create_intersection_comparison()
        plt.show()  # Display the plots
    
    def create_intersection_comparison(self):
        """Create detailed intersection comparison charts"""
        if self.metrics_df is None:
            return
        
        duration_text = f"{self.simulation_hours}H" if self.simulation_hours > 0 else "Extended"
        fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
        fig2.suptitle(f'Intersection Performance Comparison - {duration_text}', fontsize=14, fontweight='bold')
        
        time_hours = self.metrics_df['Step'] / 3600
        
        # Queue Length Comparison (Moving Average)
        window = min(100, len(self.metrics_df) // 10)  # Adaptive window size
        if window > 1:
            j1_queue_ma = self.metrics_df['J1_Queue'].rolling(window=window, center=True).mean()
            j2_queue_ma = self.metrics_df['J2_Queue'].rolling(window=window, center=True).mean()
        else:
            j1_queue_ma = self.metrics_df['J1_Queue']
            j2_queue_ma = self.metrics_df['J2_Queue']
        
        axes2[0, 0].plot(time_hours, j1_queue_ma, label='J1 (Complex)', linewidth=2, color='red')
        axes2[0, 0].plot(time_hours, j2_queue_ma, label='J2 (4-way)', linewidth=2, color='blue')
        axes2[0, 0].set_title('Queue Length Trends (Moving Average)', fontweight='bold')
        axes2[0, 0].set_xlabel('Time (Hours)')
        axes2[0, 0].set_ylabel('Average Queue Length')
        axes2[0, 0].legend()
        axes2[0, 0].grid(True, alpha=0.3)
        axes2[0, 0].set_xlim(0, max(time_hours) if len(time_hours) > 0 else 1)
        
        # Waiting Time Comparison (Moving Average)
        if window > 1:
            j1_wait_ma = self.metrics_df['J1_Waiting'].rolling(window=window, center=True).mean()
            j2_wait_ma = self.metrics_df['J2_Waiting'].rolling(window=window, center=True).mean()
        else:
            j1_wait_ma = self.metrics_df['J1_Waiting']
            j2_wait_ma = self.metrics_df['J2_Waiting']
        
        axes2[0, 1].plot(time_hours, j1_wait_ma, label='J1 (Complex)', linewidth=2, color='orange')
        axes2[0, 1].plot(time_hours, j2_wait_ma, label='J2 (4-way)', linewidth=2, color='purple')
        axes2[0, 1].set_title('Waiting Time Trends (Moving Average)', fontweight='bold')
        axes2[0, 1].set_xlabel('Time (Hours)')
        axes2[0, 1].set_ylabel('Average Waiting Time (seconds)')
        axes2[0, 1].legend()
        axes2[0, 1].grid(True, alpha=0.3)
        axes2[0, 1].set_xlim(0, max(time_hours) if len(time_hours) > 0 else 1)
        
        # Performance Metrics Bar Chart
        metrics_data = {
            'Average Queue': [self.metrics_df['J1_Queue'].mean(), self.metrics_df['J2_Queue'].mean()],
            'Max Queue': [self.metrics_df['J1_Queue'].max(), self.metrics_df['J2_Queue'].max()],
            'Average Wait (s)': [self.metrics_df['J1_Waiting'].mean(), self.metrics_df['J2_Waiting'].mean()],
            'Max Wait (s)': [self.metrics_df['J1_Waiting'].max(), self.metrics_df['J2_Waiting'].max()]
        }
        
        x = np.arange(len(metrics_data))
        width = 0.35
        
        j1_values = [metrics_data[key][0] for key in metrics_data.keys()]
        j2_values = [metrics_data[key][1] for key in metrics_data.keys()]
        
        bars1 = axes2[1, 0].bar(x - width/2, j1_values, width, label='J1 (Complex)', color='lightcoral', alpha=0.8)
        bars2 = axes2[1, 0].bar(x + width/2, j2_values, width, label='J2 (4-way)', color='lightblue', alpha=0.8)
        
        axes2[1, 0].set_title('Performance Metrics Comparison', fontweight='bold')
        axes2[1, 0].set_ylabel('Value')
        axes2[1, 0].set_xticks(x)
        axes2[1, 0].set_xticklabels(metrics_data.keys(), rotation=45)
        axes2[1, 0].legend()
        axes2[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            axes2[1, 0].annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        for bar in bars2:
            height = bar.get_height()
            axes2[1, 0].annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        
        # Performance efficiency pie chart
        total_phase_changes = self.analyze_phase_changes()
        efficiency_data = [
            self.calculate_efficiency_score(),
            10 - self.calculate_efficiency_score()
        ]
        
        colors = ['lightgreen', 'lightcoral']
        axes2[1, 1].pie(efficiency_data, labels=['Efficient', 'Inefficient'], 
                       colors=colors, autopct='%1.1f%%', startangle=90)
        axes2[1, 1].set_title(f'System Efficiency Score: {efficiency_data[0]:.1f}/10', fontweight='bold')
        
        plt.tight_layout()
        filename = f'intersection_comparison_{duration_text.lower()}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  ✓ Intersection comparison saved as '{filename}'")
    
    def export_summary_report(self):
        """Export a comprehensive summary report for optimized controller"""
        print("Generating optimized traffic analysis report...")
        
        duration_text = f"{self.simulation_hours}-HOUR" if self.simulation_hours > 0 else "EXTENDED"
        filename = f'optimized_traffic_report_{duration_text.lower()}.txt'
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("OPTIMIZED SMART TRAFFIC CONTROL SYSTEM - ANALYSIS REPORT\n")
            f.write(f"Zamboanga KCC Intersection - {duration_text} Simulation\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-"*40 + "\n")
            
            if self.metrics_df is not None:
                avg_vehicles = self.metrics_df['Vehicles'].mean()
                avg_queue = self.metrics_df['Total_Queue'].mean()
                avg_waiting = self.metrics_df['Average_Waiting'].mean()
                efficiency = self.calculate_efficiency_score()
                
                f.write(f"• Simulation Duration: {duration_text}\n")
                f.write(f"• Data Points Collected: {len(self.metrics_df):,}\n")
                f.write(f"• Average vehicles in network: {avg_vehicles:.1f}\n")
                f.write(f"• Average total queue length: {avg_queue:.2f} vehicles\n")
                f.write(f"• Average waiting time: {avg_waiting:.2f} seconds\n")
                f.write(f"• System efficiency score: {efficiency:.2f}/10\n")
                f.write(f"• Queue management rating: {self.rate_queue_management()}\n")
                f.write(f"• Traffic flow rating: {self.rate_traffic_flow()}\n")
            
            f.write("\n")
            
            # Detailed Intersection Analysis
            if self.metrics_df is not None:
                f.write("INTERSECTION PERFORMANCE ANALYSIS\n")
                f.write("-"*40 + "\n")
                
                j1_avg_queue = self.metrics_df['J1_Queue'].mean()
                j2_avg_queue = self.metrics_df['J2_Queue'].mean()
                j1_max_queue = self.metrics_df['J1_Queue'].max()
                j2_max_queue = self.metrics_df['J2_Queue'].max()
                j1_avg_wait = self.metrics_df['J1_Waiting'].mean()
                j2_avg_wait = self.metrics_df['J2_Waiting'].mean()
                
                phase_data = self.analyze_phase_changes()
                
                f.write(f"J1 (Complex Intersection):\n")
                f.write(f"  - Average queue length: {j1_avg_queue:.2f} vehicles\n")
                f.write(f"  - Maximum queue length: {j1_max_queue} vehicles\n")
                f.write(f"  - Average waiting time: {j1_avg_wait:.2f} seconds\n")
                f.write(f"  - Total phase changes: {phase_data['J1']:,}\n")
                f.write(f"  - Average time between changes: {phase_data['J1_avg_time']:.1f} seconds\n\n")
                
                f.write(f"J2 (4-Way Intersection):\n")
                f.write(f"  - Average queue length: {j2_avg_queue:.2f} vehicles\n")
                f.write(f"  - Maximum queue length: {j2_max_queue} vehicles\n")
                f.write(f"  - Average waiting time: {j2_avg_wait:.2f} seconds\n")
                f.write(f"  - Total phase changes: {phase_data['J2']:,}\n")
                f.write(f"  - Average time between changes: {phase_data['J2_avg_time']:.1f} seconds\n\n")
                
                # Performance comparison
                better_queue = "J1" if j1_avg_queue < j2_avg_queue else "J2"
                better_wait = "J1" if j1_avg_wait < j2_avg_wait else "J2"
                
                f.write(f"Performance Comparison:\n")
                f.write(f"  - Better queue management: {better_queue}\n")
                f.write(f"  - Better waiting time: {better_wait}\n")
                f.write(f"  - Queue difference: {abs(j1_avg_queue - j2_avg_queue):.2f} vehicles\n")
                f.write(f"  - Waiting time difference: {abs(j1_avg_wait - j2_avg_wait):.2f} seconds\n")
                
                # Traffic pattern analysis
                f.write(f"\nTraffic Pattern Analysis:\n")
                vehicle_std = self.metrics_df['Vehicles'].std()
                f.write(f"  - Vehicle count stability (std dev): {vehicle_std:.2f}\n")
                f.write(f"  - Peak vehicle count: {self.metrics_df['Vehicles'].max()}\n")
                f.write(f"  - Minimum vehicle count: {self.metrics_df['Vehicles'].min()}\n")
                
                # Optimization insights
                f.write(f"\nOptimization Insights:\n")
                if j1_avg_queue > j2_avg_queue:
                    f.write(f"  - J1 experiences higher congestion, consider enhanced timing\n")
                if phase_data['J1'] > phase_data['J2'] * 1.5:
                    f.write(f"  - J1 has frequent phase changes, may indicate responsive control\n")
                if avg_waiting < 10:
                    f.write(f"  - Excellent waiting times achieved through optimization\n")
                elif avg_waiting < 20:
                    f.write(f"  - Good waiting times, minor optimization possible\n")
                else:
                    f.write(f"  - Consider further parameter tuning for waiting times\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("ANALYSIS COMPLETE\n")
            f.write("="*80 + "\n")
            f.write("Files generated during analysis:\n")
            if self.is_500h_simulation:
                f.write(f"  - optimized_traffic_analysis_500h.png\n")
                f.write(f"  - intersection_comparison_500h.png\n")
                f.write(f"  - {filename}\n")
            else:
                f.write(f"  - optimized_traffic_analysis_extended.png\n")
                f.write(f"  - intersection_comparison_extended.png\n")
                f.write(f"  - {filename}\n")
            f.write("\nUse these visualizations to understand traffic patterns and system performance.\n")
        
        print(f"  ✓ Summary report saved as '{filename}'")
    
    def run_full_analysis(self):
        """Run complete analysis workflow for optimized controller"""
        print("Starting comprehensive optimized traffic analysis...\n")
        
        if not self.load_data():
            print("Failed to load data. Please ensure CSV files exist.")
            print("Expected files: traffic_metrics_500h.csv, optimized_traffic_metrics.csv, or traffic_metrics.csv")
            return
        
        # Check if we have data to analyze
        if self.metrics_df is None or len(self.metrics_df) == 0:
            print("❌ No data available for analysis!")
            print("💡 Tip: Run the optimized controller first to generate data:")
            print("   python optimized_traffic_controller.py")
            return
        
        self.generate_basic_statistics()
        print("\n")
        self.create_visualizations()
        print("\n")
        self.export_summary_report()
        
        duration_text = f"{self.simulation_hours}H" if self.simulation_hours > 0 else "Extended"
        print(f"\n{'='*70}")
        print("OPTIMIZED TRAFFIC ANALYSIS COMPLETE!")
        print(f"{'='*70}")
        print("📊 Generated analysis files:")
        print(f"  � optimized_traffic_analysis_{duration_text.lower()}.png")
        print(f"  � intersection_comparison_{duration_text.lower()}.png") 
        print(f"  📄 optimized_traffic_report_{duration_text.lower()}.txt")
        print(f"{'='*70}")
        print("🎯 Key Insights:")
        if self.metrics_df is not None:
            efficiency = self.calculate_efficiency_score()
            print(f"  • System Efficiency: {efficiency:.1f}/10 ({self.rate_traffic_flow()})")
            print(f"  • Queue Management: {self.rate_queue_management()}")
            print(f"  • Average Network Queue: {self.metrics_df['Total_Queue'].mean():.1f} vehicles")
            print(f"  • Average Waiting Time: {self.metrics_df['Average_Waiting'].mean():.1f} seconds")
        print(f"{'='*70}")

# Run analysis if executed directly
if __name__ == "__main__":
    analyzer = OptimizedTrafficAnalyzer()
    analyzer.run_full_analysis()
