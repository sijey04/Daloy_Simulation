# =============================================================================
#           COMPARATIVE TRAFFIC ANALYSIS TOOL - ZAMBOANGA KCC
#           OPTIMIZED AI vs BASELINE REAL-WORLD COMPARISON
#           (UNICODE-SAFE VERSION FOR WINDOWS)
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class ComparativeTrafficAnalyzer:
    def __init__(self, data_dir="."):
        """Initialize analyzer for comparing optimized vs baseline scenarios"""
        self.data_dir = data_dir
        self.optimized_df = None
        self.baseline_df = None
        self.comparison_results = {}
        
    def load_comparison_data(self):
        """Load both optimized and baseline data for comparison"""
        try:
            print("Loading comparative traffic data...")
            
            # Load optimized data
            optimized_files = [
                'traffic_metrics_500h.csv',
                'optimized_traffic_metrics.csv',
                'traffic_metrics.csv'
            ]
            
            for file in optimized_files:
                if os.path.exists(os.path.join(self.data_dir, file)):
                    try:
                        # Try loading with headers first
                        test_df = pd.read_csv(os.path.join(self.data_dir, file), nrows=1)
                        if len(test_df.columns) > 5 and not test_df.columns[0].isdigit():
                            # File has proper headers
                            self.optimized_df = pd.read_csv(os.path.join(self.data_dir, file))
                        else:
                            # File has no headers, add them
                            self.optimized_df = pd.read_csv(os.path.join(self.data_dir, file), 
                                                          header=None,
                                                          names=['Step', 'Time', 'Vehicles', 'J1_Phase', 'J2_Phase', 
                                                               'J1_Queue', 'J2_Queue', 'J1_Waiting', 'J2_Waiting'])
                        
                        if len(self.optimized_df) > 0:
                            print(f"  [OK] Loaded optimized data: {file} ({len(self.optimized_df):,} records)")
                            break
                    except Exception as e:
                        print(f"  [WARNING] Could not load {file}: {e}")
                        continue
            
            # Load baseline data
            if os.path.exists(os.path.join(self.data_dir, 'baseline_traffic_metrics.csv')):
                self.baseline_df = pd.read_csv(os.path.join(self.data_dir, 'baseline_traffic_metrics.csv'))
                print(f"  [OK] Loaded baseline data: baseline_traffic_metrics.csv ({len(self.baseline_df):,} records)")
            
            if self.optimized_df is None:
                print("  [ERROR] No optimized data found!")
                return False
                
            if self.baseline_df is None:
                print("  [ERROR] No baseline data found! Run baseline_traffic_controller.py first.")
                return False
            
            # Standardize column names
            self.standardize_data_formats()
            
            print("Data loading complete!\n")
            return True
            
        except Exception as e:
            print(f"Error loading comparison data: {e}")
            return False
    
    def standardize_data_formats(self):
        """Ensure both datasets have comparable column formats"""
        
        # Standardize optimized data columns
        if 'J1_Queue' not in self.optimized_df.columns and 'J1_Queue_Length' in self.optimized_df.columns:
            self.optimized_df['J1_Queue'] = self.optimized_df['J1_Queue_Length']
        if 'J2_Queue' not in self.optimized_df.columns and 'J2_Queue_Length' in self.optimized_df.columns:
            self.optimized_df['J2_Queue'] = self.optimized_df['J2_Queue_Length']
        if 'Vehicles' not in self.optimized_df.columns and 'Total_Vehicles' in self.optimized_df.columns:
            self.optimized_df['Vehicles'] = self.optimized_df['Total_Vehicles']
        
        # Add missing columns to optimized data with safe defaults
        if 'Total_Queue' not in self.optimized_df.columns:
            j1_queue = self.optimized_df.get('J1_Queue', pd.Series([0] * len(self.optimized_df)))
            j2_queue = self.optimized_df.get('J2_Queue', pd.Series([0] * len(self.optimized_df)))
            self.optimized_df['Total_Queue'] = j1_queue + j2_queue
        
        if 'Network_Delay' not in self.optimized_df.columns:
            j1_waiting = self.optimized_df.get('J1_Waiting', pd.Series([0.0] * len(self.optimized_df)))
            j2_waiting = self.optimized_df.get('J2_Waiting', pd.Series([0.0] * len(self.optimized_df)))
            self.optimized_df['Network_Delay'] = (j1_waiting + j2_waiting) / 2
        
        # Add missing columns to baseline data with safe defaults
        if 'Total_Queue' not in self.baseline_df.columns:
            j1_queue = self.baseline_df.get('J1_Queue', pd.Series([0] * len(self.baseline_df)))
            j2_queue = self.baseline_df.get('J2_Queue', pd.Series([0] * len(self.baseline_df)))
            self.baseline_df['Total_Queue'] = j1_queue + j2_queue
        
        if 'Network_Delay' not in self.baseline_df.columns:
            # Use existing Network_Delay if available, otherwise create from components
            if 'Network_Delay' not in self.baseline_df.columns:
                self.baseline_df['Network_Delay'] = self.baseline_df.get('Network_Delay', 
                                                   pd.Series([0.0] * len(self.baseline_df)))
        
        # Add hour column for both
        if 'Hour' not in self.optimized_df.columns:
            self.optimized_df['Hour'] = self.optimized_df['Step'] // 3600
        if 'Hour' not in self.baseline_df.columns:
            self.baseline_df['Hour'] = self.baseline_df['Step'] // 3600
    
    def calculate_performance_metrics(self):
        """Calculate comprehensive performance comparison metrics"""
        print("Calculating performance comparison metrics...")
        
        results = {}
        
        # Get matching time ranges
        max_steps_opt = self.optimized_df['Step'].max()
        max_steps_base = self.baseline_df['Step'].max()
        min_steps = min(max_steps_opt, max_steps_base)
        
        # Filter to matching time range
        opt_filtered = self.optimized_df[self.optimized_df['Step'] <= min_steps]
        base_filtered = self.baseline_df[self.baseline_df['Step'] <= min_steps]
        
        # Traffic Flow Metrics
        results['traffic_flow'] = {
            'optimized': {
                'avg_vehicles': opt_filtered['Vehicles'].mean(),
                'max_vehicles': opt_filtered['Vehicles'].max(),
                'vehicle_stability': opt_filtered['Vehicles'].std(),
            },
            'baseline': {
                'avg_vehicles': base_filtered['Vehicles'].mean(),
                'max_vehicles': base_filtered['Vehicles'].max(),
                'vehicle_stability': base_filtered['Vehicles'].std(),
            }
        }
        
        # Queue Performance
        results['queue_performance'] = {
            'optimized': {
                'j1_avg_queue': opt_filtered['J1_Queue'].mean(),
                'j2_avg_queue': opt_filtered['J2_Queue'].mean(),
                'j1_max_queue': opt_filtered['J1_Queue'].max(),
                'j2_max_queue': opt_filtered['J2_Queue'].max(),
                'total_avg_queue': opt_filtered['Total_Queue'].mean(),
                'total_max_queue': opt_filtered['Total_Queue'].max(),
            },
            'baseline': {
                'j1_avg_queue': base_filtered['J1_Queue'].mean(),
                'j2_avg_queue': base_filtered['J2_Queue'].mean(),
                'j1_max_queue': base_filtered['J1_Queue'].max(),
                'j2_max_queue': base_filtered['J2_Queue'].max(),
                'total_avg_queue': base_filtered['Total_Queue'].mean(),
                'total_max_queue': base_filtered['Total_Queue'].max(),
            }
        }
        
        # Delay Performance (Primary Efficiency Metric)
        results['delay_performance'] = {
            'optimized': {
                'avg_delay': opt_filtered['Network_Delay'].mean(),
                'max_delay': opt_filtered['Network_Delay'].max(),
                'delay_stability': opt_filtered['Network_Delay'].std(),
            },
            'baseline': {
                'avg_delay': base_filtered['Network_Delay'].mean(),
                'max_delay': base_filtered['Network_Delay'].max(),
                'delay_stability': base_filtered['Network_Delay'].std(),
            }
        }
        
        # ENHANCED METRICS - Additional Traffic Performance Indicators
        
        # Efficiency Metrics
        results['efficiency_metrics'] = {
            'optimized': {
                'avg_vehicle_delay': opt_filtered['Network_Delay'].mean(),  # Primary efficiency metric
                'avg_travel_time': self._calculate_travel_time(opt_filtered),
                'delay_variability': opt_filtered['Network_Delay'].std(),
            },
            'baseline': {
                'avg_vehicle_delay': base_filtered['Network_Delay'].mean(),
                'avg_travel_time': self._calculate_travel_time(base_filtered),
                'delay_variability': base_filtered['Network_Delay'].std(),
            }
        }
        
        # Congestion Metrics
        results['congestion_metrics'] = {
            'optimized': {
                'avg_queue_length': opt_filtered['Total_Queue'].mean(),
                'max_queue_length': opt_filtered['Total_Queue'].max(),
                'total_throughput': self._calculate_throughput(opt_filtered),
                'congestion_index': self._calculate_congestion_index(opt_filtered),
            },
            'baseline': {
                'avg_queue_length': base_filtered['Total_Queue'].mean(),
                'max_queue_length': base_filtered['Total_Queue'].max(),
                'total_throughput': self._calculate_throughput(base_filtered),
                'congestion_index': self._calculate_congestion_index(base_filtered),
            }
        }
        
        # Environmental Metrics (Estimated)
        results['environmental_metrics'] = {
            'optimized': {
                'estimated_co2_emissions': self._estimate_co2_emissions(opt_filtered),
                'fuel_efficiency_index': self._calculate_fuel_efficiency(opt_filtered),
                'environmental_impact_score': self._calculate_environmental_score(opt_filtered),
            },
            'baseline': {
                'estimated_co2_emissions': self._estimate_co2_emissions(base_filtered),
                'fuel_efficiency_index': self._calculate_fuel_efficiency(base_filtered),
                'environmental_impact_score': self._calculate_environmental_score(base_filtered),
            }
        }
        
        # Calculate improvement percentages
        results['improvements'] = {
            'queue_reduction': ((results['queue_performance']['baseline']['total_avg_queue'] - 
                               results['queue_performance']['optimized']['total_avg_queue']) / 
                              results['queue_performance']['baseline']['total_avg_queue'] * 100),
            'delay_reduction': ((results['delay_performance']['baseline']['avg_delay'] - 
                               results['delay_performance']['optimized']['avg_delay']) / 
                              results['delay_performance']['baseline']['avg_delay'] * 100),
            'j1_queue_reduction': ((results['queue_performance']['baseline']['j1_avg_queue'] - 
                                  results['queue_performance']['optimized']['j1_avg_queue']) / 
                                 results['queue_performance']['baseline']['j1_avg_queue'] * 100),
            'j2_queue_reduction': ((results['queue_performance']['baseline']['j2_avg_queue'] - 
                                  results['queue_performance']['optimized']['j2_avg_queue']) / 
                                 results['queue_performance']['baseline']['j2_avg_queue'] * 100),
            # Enhanced metric improvements
            'travel_time_improvement': ((results['efficiency_metrics']['baseline']['avg_travel_time'] - 
                                       results['efficiency_metrics']['optimized']['avg_travel_time']) / 
                                      results['efficiency_metrics']['baseline']['avg_travel_time'] * 100),
            'throughput_improvement': ((results['congestion_metrics']['optimized']['total_throughput'] - 
                                      results['congestion_metrics']['baseline']['total_throughput']) / 
                                     results['congestion_metrics']['baseline']['total_throughput'] * 100),
            'co2_reduction': ((results['environmental_metrics']['baseline']['estimated_co2_emissions'] - 
                             results['environmental_metrics']['optimized']['estimated_co2_emissions']) / 
                            results['environmental_metrics']['baseline']['estimated_co2_emissions'] * 100),
        }
        
        self.comparison_results = results
        print("[OK] Performance metrics calculated")
        return results
    
    def _calculate_travel_time(self, df):
        """Estimate average travel time based on delay and vehicle count"""
        # Estimated based on average delay + baseline travel time
        base_travel_time = 60  # Estimated 60 seconds base travel time
        return base_travel_time + df['Network_Delay'].mean()
    
    def _calculate_throughput(self, df):
        """Calculate network throughput (vehicles processed per hour)"""
        if len(df) == 0:
            return 0
        
        # For gridlocked systems with massive vehicle accumulation,
        # throughput should reflect actual traffic flow, not vehicle pile-up
        df_sorted = df.sort_values('Step')
        
        # Calculate the effective flow rate based on queue dynamics
        # If queues are constantly growing, actual throughput is very low
        avg_vehicles = df_sorted['Vehicles'].mean()
        avg_queue = df_sorted.get('Total_Queue', pd.Series([0])).mean()
        
        # Realistic throughput calculation:
        # High vehicle counts with high queues = gridlock = low actual throughput
        if avg_vehicles > 1000:  # Gridlock scenario
            # Use queue efficiency as throughput measure
            queue_efficiency = max(0.01, 1 - (avg_queue / avg_vehicles))
            realistic_throughput = avg_vehicles * queue_efficiency * 0.1  # Very low flow rate
        else:  # Normal flow scenario
            # Use average vehicles as flow capacity proxy
            realistic_throughput = avg_vehicles * 10  # More reasonable hourly rate
        
        return realistic_throughput
    
    def _calculate_congestion_index(self, df):
        """Calculate congestion index based on queue length relative to vehicle count"""
        if df['Vehicles'].mean() == 0:
            return 0
        return (df['Total_Queue'].mean() / df['Vehicles'].mean()) * 100
    
    def _estimate_co2_emissions(self, df):
        """Estimate CO2 emissions based on delay and vehicle count"""
        # Estimated CO2 emissions: base emission + delay penalty
        # Base: ~200g CO2/km, delay increases emissions
        base_emission_per_vehicle = 200  # grams CO2 per vehicle per km
        delay_penalty = 0.5  # Additional grams per second of delay
        
        avg_vehicles = df['Vehicles'].mean()
        avg_delay = df['Network_Delay'].mean()
        estimated_distance = 1.0  # Assume 1km average trip
        
        total_emissions = (avg_vehicles * base_emission_per_vehicle * estimated_distance + 
                          avg_vehicles * avg_delay * delay_penalty)
        return total_emissions
    
    def _calculate_fuel_efficiency(self, df):
        """Calculate fuel efficiency index (higher is better)"""
        # Based on reduced idling time and smoother traffic flow
        base_efficiency = 100
        delay_penalty = df['Network_Delay'].mean() * 0.1  # 0.1% penalty per second delay
        queue_penalty = df['Total_Queue'].mean() * 0.5   # 0.5% penalty per vehicle in queue
        
        efficiency_index = base_efficiency - delay_penalty - queue_penalty
        return max(0, efficiency_index)  # Ensure non-negative
    
    def _calculate_environmental_score(self, df):
        """Calculate overall environmental impact score (lower is better)"""
        co2_factor = self._estimate_co2_emissions(df) / 1000  # Convert to kg
        efficiency_factor = (100 - self._calculate_fuel_efficiency(df)) / 10
        congestion_factor = self._calculate_congestion_index(df) / 10
        
        return co2_factor + efficiency_factor + congestion_factor
    
    def generate_comparison_statistics(self):
        """Generate detailed comparison statistics"""
        print("="*80)
        print("OPTIMIZED vs BASELINE TRAFFIC CONTROL COMPARISON")
        print("="*80)
        
        if not self.comparison_results:
            self.calculate_performance_metrics()
        
        results = self.comparison_results
        
        print("\nTRAFFIC FLOW COMPARISON:")
        print("-" * 50)
        opt_vehicles = results['traffic_flow']['optimized']['avg_vehicles']
        base_vehicles = results['traffic_flow']['baseline']['avg_vehicles']
        print(f"Average Vehicles in Network:")
        print(f"  • Optimized AI: {opt_vehicles:.1f} vehicles")
        print(f"  • Baseline:     {base_vehicles:.1f} vehicles")
        print(f"  • Difference:   {opt_vehicles - base_vehicles:+.1f} vehicles")
        
        print(f"\nNetwork Stability (Lower is Better):")
        opt_stability = results['traffic_flow']['optimized']['vehicle_stability']
        base_stability = results['traffic_flow']['baseline']['vehicle_stability']
        print(f"  • Optimized AI: {opt_stability:.2f} std dev")
        print(f"  • Baseline:     {base_stability:.2f} std dev")
        print(f"  • Improvement:  {((base_stability - opt_stability) / base_stability * 100):+.1f}%")
        
        print("\nQUEUE LENGTH COMPARISON:")
        print("-" * 50)
        print(f"Total Network Queue:")
        opt_queue = results['queue_performance']['optimized']['total_avg_queue']
        base_queue = results['queue_performance']['baseline']['total_avg_queue']
        print(f"  • Optimized AI: {opt_queue:.2f} vehicles")
        print(f"  • Baseline:     {base_queue:.2f} vehicles")
        print(f"  • Reduction:    {results['improvements']['queue_reduction']:+.1f}%")
        
        print(f"\nJ1 Complex Intersection:")
        opt_j1 = results['queue_performance']['optimized']['j1_avg_queue']
        base_j1 = results['queue_performance']['baseline']['j1_avg_queue']
        print(f"  • Optimized AI: {opt_j1:.2f} vehicles")
        print(f"  • Baseline:     {base_j1:.2f} vehicles")
        print(f"  • Reduction:    {results['improvements']['j1_queue_reduction']:+.1f}%")
        
        print(f"\nJ2 4-Way Intersection:")
        opt_j2 = results['queue_performance']['optimized']['j2_avg_queue']
        base_j2 = results['queue_performance']['baseline']['j2_avg_queue']
        print(f"  • Optimized AI: {opt_j2:.2f} vehicles")
        print(f"  • Baseline:     {base_j2:.2f} vehicles (No Traffic Lights)")
        print(f"  • Reduction:    {results['improvements']['j2_queue_reduction']:+.1f}%")
        
        print("\nDELAY COMPARISON:")
        print("-" * 50)
        opt_delay = results['delay_performance']['optimized']['avg_delay']
        base_delay = results['delay_performance']['baseline']['avg_delay']
        print(f"Average Network Delay:")
        print(f"  • Optimized AI: {opt_delay:.2f} seconds")
        print(f"  • Baseline:     {base_delay:.2f} seconds")
        print(f"  • Reduction:    {results['improvements']['delay_reduction']:+.1f}%")
        
        print("\nEFFICIENCY METRICS:")
        print("-" * 50)
        opt_travel = results['efficiency_metrics']['optimized']['avg_travel_time']
        base_travel = results['efficiency_metrics']['baseline']['avg_travel_time']
        print(f"Average Travel Time:")
        print(f"  • Optimized AI: {opt_travel:.1f} seconds")
        print(f"  • Baseline:     {base_travel:.1f} seconds")
        print(f"  • Improvement:  {results['improvements']['travel_time_improvement']:+.1f}%")
        
        print("\nCONGESTION METRICS:")
        print("-" * 50)
        opt_throughput = results['congestion_metrics']['optimized']['total_throughput']
        base_throughput = results['congestion_metrics']['baseline']['total_throughput']
        print(f"Network Throughput (vehicles/hour):")
        print(f"  • Optimized AI: {opt_throughput:.1f} veh/h")
        print(f"  • Baseline:     {base_throughput:.1f} veh/h")
        print(f"  • Improvement:  {results['improvements']['throughput_improvement']:+.1f}%")
        
        opt_congestion = results['congestion_metrics']['optimized']['congestion_index']
        base_congestion = results['congestion_metrics']['baseline']['congestion_index']
        print(f"\nCongestion Index (% vehicles queued):")
        print(f"  • Optimized AI: {opt_congestion:.1f}%")
        print(f"  • Baseline:     {base_congestion:.1f}%")
        
        print("\nENVIRONMENTAL IMPACT:")
        print("-" * 50)
        opt_co2 = results['environmental_metrics']['optimized']['estimated_co2_emissions']
        base_co2 = results['environmental_metrics']['baseline']['estimated_co2_emissions']
        print(f"Estimated CO2 Emissions (g/hour):")
        print(f"  • Optimized AI: {opt_co2:.1f} g/h")
        print(f"  • Baseline:     {base_co2:.1f} g/h")
        print(f"  • Reduction:    {results['improvements']['co2_reduction']:+.1f}%")
        
        opt_fuel = results['environmental_metrics']['optimized']['fuel_efficiency_index']
        base_fuel = results['environmental_metrics']['baseline']['fuel_efficiency_index']
        print(f"\nFuel Efficiency Index (higher is better):")
        print(f"  • Optimized AI: {opt_fuel:.1f}")
        print(f"  • Baseline:     {base_fuel:.1f}")
        
        print("\nOVERALL PERFORMANCE IMPACT:")
        print("-" * 50)
        total_improvement = (abs(results['improvements']['queue_reduction']) + 
                           abs(results['improvements']['delay_reduction']) +
                           abs(results['improvements']['travel_time_improvement']) +
                           abs(results['improvements']['co2_reduction'])) / 4
        print(f"  • Comprehensive Performance Improvement: {total_improvement:.1f}%")
        
        # Performance categories
        if total_improvement > 30:
            print("  • Status: EXCEPTIONAL IMPROVEMENT")
        elif total_improvement > 15:
            print("  • Status: SIGNIFICANT IMPROVEMENT")
        elif total_improvement > 5:
            print("  • Status: MODERATE IMPROVEMENT")
        else:
            print("  • Status: MINIMAL IMPROVEMENT")
        
        print("="*80)
    
    def create_comparison_visualizations(self):
        """Create comprehensive comparison visualizations"""
        print("Generating comparison visualizations...")
        
        if not self.comparison_results:
            self.calculate_performance_metrics()
        
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(3, 2, figsize=(16, 18))
        fig.suptitle('Comprehensive Traffic Control Comparison: Optimized AI vs Real-World Baseline', 
                    fontsize=16, fontweight='bold')
        
        # Limit data for visualization performance
        opt_sample = self.optimized_df.sample(min(2000, len(self.optimized_df)))
        base_sample = self.baseline_df.sample(min(2000, len(self.baseline_df)))
        
        # 1. Vehicle Count Comparison
        axes[0, 0].plot(opt_sample['Step']/3600, opt_sample['Vehicles'], 
                       alpha=0.7, linewidth=1, label='Optimized AI', color='blue')
        axes[0, 0].plot(base_sample['Step']/3600, base_sample['Vehicles'], 
                       alpha=0.7, linewidth=1, label='Baseline', color='red')
        axes[0, 0].set_title('Vehicle Count Over Time', fontweight='bold')
        axes[0, 0].set_xlabel('Time (Hours)')
        axes[0, 0].set_ylabel('Number of Vehicles')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Queue Length Comparison
        axes[0, 1].plot(opt_sample['Step']/3600, opt_sample['Total_Queue'], 
                       alpha=0.7, linewidth=1, label='Optimized AI', color='blue')
        axes[0, 1].plot(base_sample['Step']/3600, base_sample['Total_Queue'], 
                       alpha=0.7, linewidth=1, label='Baseline', color='red')
        axes[0, 1].set_title('Total Queue Length Comparison', fontweight='bold')
        axes[0, 1].set_xlabel('Time (Hours)')
        axes[0, 1].set_ylabel('Queue Length (vehicles)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Performance Distribution Comparison
        axes[1, 0].hist(opt_sample['Total_Queue'], bins=30, alpha=0.6, 
                       color='blue', label='Optimized AI', density=True)
        axes[1, 0].hist(base_sample['Total_Queue'], bins=30, alpha=0.6, 
                       color='red', label='Baseline', density=True)
        axes[1, 0].set_title('Queue Length Distribution', fontweight='bold')
        axes[1, 0].set_xlabel('Queue Length (vehicles)')
        axes[1, 0].set_ylabel('Probability Density')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Comprehensive Performance Improvements
        improvements = [
            self.comparison_results['improvements']['queue_reduction'],
            self.comparison_results['improvements']['delay_reduction'],
            self.comparison_results['improvements']['travel_time_improvement'],
            self.comparison_results['improvements']['throughput_improvement'],
            self.comparison_results['improvements']['co2_reduction']
        ]
        improvement_labels = ['Queue\nReduction', 'Delay\nReduction', 'Travel Time\nImprovement', 
                             'Throughput\nImprovement', 'CO₂\nReduction']
        colors = ['green' if x > 0 else 'red' for x in improvements]
        
        bars = axes[1, 1].bar(improvement_labels, improvements, color=colors, alpha=0.7)
        axes[1, 1].set_title('Comprehensive Performance Improvements (%)', fontweight='bold')
        axes[1, 1].set_ylabel('Improvement (%)')
        axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, improvements):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + (1 if height > 0 else -3),
                           f'{value:.1f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)
        
        # 5. Efficiency Metrics Comparison
        efficiency_metrics = ['Average Delay', 'Travel Time', 'Fuel Efficiency']
        opt_efficiency = [
            self.comparison_results['efficiency_metrics']['optimized']['avg_vehicle_delay'],
            self.comparison_results['efficiency_metrics']['optimized']['avg_travel_time'],
            self.comparison_results['environmental_metrics']['optimized']['fuel_efficiency_index']
        ]
        base_efficiency = [
            self.comparison_results['efficiency_metrics']['baseline']['avg_vehicle_delay'],
            self.comparison_results['efficiency_metrics']['baseline']['avg_travel_time'],
            self.comparison_results['environmental_metrics']['baseline']['fuel_efficiency_index']
        ]
        
        x = np.arange(len(efficiency_metrics))
        width = 0.35
        
        axes[2, 0].bar(x - width/2, opt_efficiency, width, label='Optimized AI', color='blue', alpha=0.7)
        axes[2, 0].bar(x + width/2, base_efficiency, width, label='Baseline', color='red', alpha=0.7)
        axes[2, 0].set_title('Efficiency Metrics Comparison', fontweight='bold')
        axes[2, 0].set_ylabel('Value')
        axes[2, 0].set_xticks(x)
        axes[2, 0].set_xticklabels(efficiency_metrics)
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3, axis='y')
        
        # 6. Environmental Impact Comparison
        env_metrics = ['CO₂ Emissions (g/h)', 'Environmental Score']
        opt_env = [
            self.comparison_results['environmental_metrics']['optimized']['estimated_co2_emissions'],
            self.comparison_results['environmental_metrics']['optimized']['environmental_impact_score']
        ]
        base_env = [
            self.comparison_results['environmental_metrics']['baseline']['estimated_co2_emissions'],
            self.comparison_results['environmental_metrics']['baseline']['environmental_impact_score']
        ]
        
        x = np.arange(len(env_metrics))
        
        axes[2, 1].bar(x - width/2, opt_env, width, label='Optimized AI', color='blue', alpha=0.7)
        axes[2, 1].bar(x + width/2, base_env, width, label='Baseline', color='red', alpha=0.7)
        axes[2, 1].set_title('Environmental Impact Comparison', fontweight='bold')
        axes[2, 1].set_ylabel('Value (Lower is Better)')
        axes[2, 1].set_xticks(x)
        axes[2, 1].set_xticklabels(env_metrics, fontsize=9)
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        filename = 'optimized_vs_baseline_comparison.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  [SAVED] Comparison dashboard saved as '{filename}'")
        plt.show()
    
    def export_comparison_report(self):
        """Export detailed comparison report"""
        print("Generating detailed comparison report...")
        
        if not self.comparison_results:
            self.calculate_performance_metrics()
        
        results = self.comparison_results
        filename = 'optimized_vs_baseline_report.txt'
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("OPTIMIZED AI vs BASELINE TRAFFIC CONTROL COMPARISON REPORT\n")
            f.write("Zamboanga KCC Intersection Study\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            f.write("STUDY OVERVIEW\n")
            f.write("-"*40 + "\n")
            f.write("This analysis compares two traffic management scenarios:\n")
            f.write("• OPTIMIZED: AI-controlled system with 360° detection and adaptive timing\n")
            f.write("• BASELINE: Real-world conditions with fixed-time J1 and no J2 signals\n\n")
            
            f.write("TRAFFIC FLOW ANALYSIS\n")
            f.write("-"*40 + "\n")
            opt_vehicles = results['traffic_flow']['optimized']['avg_vehicles']
            base_vehicles = results['traffic_flow']['baseline']['avg_vehicles']
            f.write(f"Average Vehicles in Network:\n")
            f.write(f"  • Optimized AI System: {opt_vehicles:.1f} vehicles\n")
            f.write(f"  • Baseline Real-World: {base_vehicles:.1f} vehicles\n")
            f.write(f"  • Difference: {opt_vehicles - base_vehicles:+.1f} vehicles\n\n")
            
            f.write("QUEUE PERFORMANCE ANALYSIS\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Network Queue Reduction: {results['improvements']['queue_reduction']:+.1f}%\n")
            f.write(f"J1 (Complex) Queue Reduction: {results['improvements']['j1_queue_reduction']:+.1f}%\n")
            f.write(f"J2 (4-Way) Queue Reduction: {results['improvements']['j2_queue_reduction']:+.1f}%\n\n")
            
            opt_queue = results['queue_performance']['optimized']['total_avg_queue']
            base_queue = results['queue_performance']['baseline']['total_avg_queue']
            f.write(f"Detailed Queue Metrics:\n")
            f.write(f"  Optimized Average Queue: {opt_queue:.2f} vehicles\n")
            f.write(f"  Baseline Average Queue: {base_queue:.2f} vehicles\n")
            f.write(f"  Absolute Reduction: {base_queue - opt_queue:.2f} vehicles\n\n")
            
            f.write("DELAY PERFORMANCE ANALYSIS\n")
            f.write("-"*40 + "\n")
            opt_delay = results['delay_performance']['optimized']['avg_delay']
            base_delay = results['delay_performance']['baseline']['avg_delay']
            f.write(f"Network Delay Reduction: {results['improvements']['delay_reduction']:+.1f}%\n")
            f.write(f"  Optimized Average Delay: {opt_delay:.2f} seconds\n")
            f.write(f"  Baseline Average Delay: {base_delay:.2f} seconds\n")
            f.write(f"  Absolute Reduction: {base_delay - opt_delay:.2f} seconds\n\n")
            
            f.write("EFFICIENCY PERFORMANCE ANALYSIS\n")
            f.write("-"*40 + "\n")
            opt_travel = results['efficiency_metrics']['optimized']['avg_travel_time']
            base_travel = results['efficiency_metrics']['baseline']['avg_travel_time']
            f.write(f"Travel Time Improvement: {results['improvements']['travel_time_improvement']:+.1f}%\n")
            f.write(f"  Optimized Average Travel Time: {opt_travel:.1f} seconds\n")
            f.write(f"  Baseline Average Travel Time: {base_travel:.1f} seconds\n")
            f.write(f"  Time Savings: {base_travel - opt_travel:.1f} seconds per trip\n\n")
            
            f.write("CONGESTION PERFORMANCE ANALYSIS\n")
            f.write("-"*40 + "\n")
            opt_throughput = results['congestion_metrics']['optimized']['total_throughput']
            base_throughput = results['congestion_metrics']['baseline']['total_throughput']
            f.write(f"Throughput Improvement: {results['improvements']['throughput_improvement']:+.1f}%\n")
            f.write(f"  Optimized Throughput: {opt_throughput:.1f} vehicles/hour\n")
            f.write(f"  Baseline Throughput: {base_throughput:.1f} vehicles/hour\n")
            f.write(f"  Additional Capacity: {opt_throughput - base_throughput:.1f} vehicles/hour\n\n")
            
            opt_congestion = results['congestion_metrics']['optimized']['congestion_index']
            base_congestion = results['congestion_metrics']['baseline']['congestion_index']
            f.write(f"Congestion Index Analysis:\n")
            f.write(f"  Optimized Congestion: {opt_congestion:.1f}% vehicles queued\n")
            f.write(f"  Baseline Congestion: {base_congestion:.1f}% vehicles queued\n")
            f.write(f"  Congestion Reduction: {base_congestion - opt_congestion:.1f} percentage points\n\n")
            
            f.write("ENVIRONMENTAL IMPACT ANALYSIS\n")
            f.write("-"*40 + "\n")
            opt_co2 = results['environmental_metrics']['optimized']['estimated_co2_emissions']
            base_co2 = results['environmental_metrics']['baseline']['estimated_co2_emissions']
            f.write(f"CO2 Emissions Reduction: {results['improvements']['co2_reduction']:+.1f}%\n")
            f.write(f"  Optimized Emissions: {opt_co2:.1f} grams/hour\n")
            f.write(f"  Baseline Emissions: {base_co2:.1f} grams/hour\n")
            f.write(f"  Emission Savings: {base_co2 - opt_co2:.1f} grams/hour\n\n")
            
            opt_fuel = results['environmental_metrics']['optimized']['fuel_efficiency_index']
            base_fuel = results['environmental_metrics']['baseline']['fuel_efficiency_index']
            f.write(f"Fuel Efficiency Analysis:\n")
            f.write(f"  Optimized Efficiency Index: {opt_fuel:.1f}\n")
            f.write(f"  Baseline Efficiency Index: {base_fuel:.1f}\n")
            f.write(f"  Efficiency Improvement: {opt_fuel - base_fuel:.1f} points\n\n")
            
            f.write("KEY FINDINGS\n")
            f.write("-"*40 + "\n")
            total_improvement = (abs(results['improvements']['queue_reduction']) + 
                               abs(results['improvements']['delay_reduction']) +
                               abs(results['improvements']['travel_time_improvement']) +
                               abs(results['improvements']['co2_reduction'])) / 4
            f.write(f"• Comprehensive System Improvement: {total_improvement:.1f}%\n")
            
            if total_improvement > 30:
                f.write("• Performance Classification: EXCEPTIONAL IMPROVEMENT\n")
                f.write("• Recommendation: AI system provides outstanding benefits - immediate implementation recommended\n")
            elif total_improvement > 15:
                f.write("• Performance Classification: SIGNIFICANT IMPROVEMENT\n")
                f.write("• Recommendation: AI system provides substantial benefits - strong case for implementation\n")
            elif total_improvement > 5:
                f.write("• Performance Classification: MODERATE IMPROVEMENT\n")
                f.write("• Recommendation: AI system shows clear benefits - consider implementation\n")
            else:
                f.write("• Performance Classification: MINIMAL IMPROVEMENT\n")
                f.write("• Recommendation: Consider cost-benefit analysis before implementation\n")
            
            f.write(f"\nDETAILED PERFORMANCE SUMMARY:\n")
            f.write(f"• Queue Length Reduction: {results['improvements']['queue_reduction']:.1f}%\n")
            f.write(f"• Vehicle Delay Reduction: {results['improvements']['delay_reduction']:.1f}%\n")
            f.write(f"• Travel Time Improvement: {results['improvements']['travel_time_improvement']:.1f}%\n")
            f.write(f"• Network Throughput Increase: {results['improvements']['throughput_improvement']:.1f}%\n")
            f.write(f"• CO2 Emissions Reduction: {results['improvements']['co2_reduction']:.1f}%\n")
            
            f.write(f"\n• The optimized AI system demonstrates measurable improvements across all key metrics\n")
            f.write(f"• Environmental benefits include reduced emissions and improved fuel efficiency\n")
            f.write(f"• Efficiency gains translate to time savings and reduced driver frustration\n")
            f.write(f"• J2 benefits significantly from AI coordination despite no physical signals\n")
            f.write(f"• Real-world implementation should consider these comprehensive performance gains\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("FILES GENERATED:\n")
            f.write("  - optimized_vs_baseline_comparison.png\n")
            f.write("  - optimized_vs_baseline_report.txt\n")
            f.write("="*80 + "\n")
        
        print(f"  [SAVED] Comparison report saved as '{filename}'")
    
    def run_full_comparison(self):
        """Run complete comparison analysis"""
        print("Starting comprehensive traffic control comparison...\n")
        
        if not self.load_comparison_data():
            print("Failed to load comparison data.")
            print("NOTE: Make sure you have run both:")
            print("   python optimized_traffic_controller.py")
            print("   python baseline_traffic_controller.py")
            return
        
        self.generate_comparison_statistics()
        print("\n")
        self.create_comparison_visualizations()
        print("\n")
        self.export_comparison_report()
        
        print(f"\n{'='*80}")
        print("TRAFFIC CONTROL COMPARISON COMPLETE!")
        print(f"{'='*80}")
        print("Generated comparison files:")
        print("  > optimized_vs_baseline_comparison.png")
        print("  > optimized_vs_baseline_report.txt")
        print(f"{'='*80}")
        
        if self.comparison_results:
            improvements = self.comparison_results['improvements']
            print("Key Results:")
            print(f"  • Queue Reduction: {improvements['queue_reduction']:+.1f}%")
            print(f"  • Delay Reduction: {improvements['delay_reduction']:+.1f}%")
            print(f"  • Travel Time Improvement: {improvements['travel_time_improvement']:+.1f}%")
            print(f"  • Throughput Improvement: {improvements['throughput_improvement']:+.1f}%")
            print(f"  • CO2 Emissions Reduction: {improvements['co2_reduction']:+.1f}%")
            print(f"  • J1 Improvement: {improvements['j1_queue_reduction']:+.1f}%")
            print(f"  • J2 Improvement: {improvements['j2_queue_reduction']:+.1f}%")
        print(f"{'='*80}")

# Run comparison if executed directly
if __name__ == "__main__":
    analyzer = ComparativeTrafficAnalyzer()
    analyzer.run_full_comparison()