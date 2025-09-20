# =============================================================================
#      INTEGRATED TRAFFIC CONTROL COMPARISON RUNNER - ZAMBOANGA KCC
#         AUTOMATED TESTING: OPTIMIZED AI vs REAL-WORLD BASELINE
# =============================================================================

import os
import sys
import subprocess
import time
from datetime import datetime

class IntegratedComparisonRunner:
    def __init__(self):
        """Initialize the integrated runner for comparison testing"""
        self.simulation_status = {
            'optimized': False,
            'baseline': False,
            'comparison': False
        }
        
    def check_requirements(self):
        """Check if all required files are present"""
        print("Checking system requirements...")
        
        required_files = [
            'optimized_traffic_controller.py',
            'baseline_traffic_controller.py',
            'comparative_analyzer.py',
            'KCCIntersection.sumocfg',
            'KCCIntersection_baseline.sumocfg'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
            else:
                print(f"  [OK] {file}")
        
        if missing_files:
            print("\n[ERROR] Missing required files:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        print("[OK] All required files present\n")
        return True
    
    def check_existing_data(self):
        """Check what simulation data already exists"""
        print("Checking existing simulation data...")
        
        # Check for optimized data
        optimized_files = [
            'traffic_metrics_500h.csv',
            'optimized_traffic_metrics.csv',
            'traffic_metrics.csv'
        ]
        
        optimized_exists = any(os.path.exists(f) for f in optimized_files)
        baseline_exists = os.path.exists('baseline_traffic_metrics.csv')
        
        if optimized_exists:
            print("  [OK] Optimized simulation data found")
            self.simulation_status['optimized'] = True
        else:
            print("  [PENDING] Optimized simulation data not found")
        
        if baseline_exists:
            print("  [OK] Baseline simulation data found")
            self.simulation_status['baseline'] = True
        else:
            print("  [PENDING] Baseline simulation data not found")
        
        print("")
        return optimized_exists, baseline_exists
    
    def run_optimized_simulation(self):
        """Run the optimized AI traffic controller simulation"""
        print("="*60)
        print("RUNNING OPTIMIZED AI SIMULATION")
        print("="*60)
        print("Starting 500-hour AI-optimized traffic simulation...")
        print("WARNING: This may take 15-20 minutes depending on your system")
        print("Expected features:")
        print("  • 360° vehicle detection")
        print("  • Adaptive signal timing")
        print("  • Real-time traffic coordination")
        print("  • Smart queue management")
        print("-"*60)
        
        try:
            start_time = time.time()
            print("Launching optimized simulation...")
            # Use Popen for better GUI compatibility
            process = subprocess.Popen([
                sys.executable, 'optimized_traffic_controller.py'
            ], shell=True)
            
            # Wait for completion with timeout
            try:
                process.wait(timeout=1800)  # 30-minute timeout
                elapsed = time.time() - start_time
                if process.returncode == 0:
                    print(f"[SUCCESS] Optimized simulation completed in {elapsed/60:.1f} minutes")
                    self.simulation_status['optimized'] = True
                    return True
                else:
                    print(f"[ERROR] Optimized simulation failed with return code: {process.returncode}")
                    return False
            except subprocess.TimeoutExpired:
                print("[TIMEOUT] Optimized simulation timed out (30 minutes)")
                process.terminate()
                return False
                
        except Exception as e:
            print(f"[ERROR] Error running optimized simulation: {e}")
            return False
    
    def run_baseline_simulation(self):
        """Run the baseline real-world traffic simulation"""
        print("="*60)
        print("RUNNING BASELINE REAL-WORLD SIMULATION")
        print("="*60)
        print("Starting 500-hour baseline traffic simulation...")
        print("WARNING: This may take 15-20 minutes depending on your system")
        print("Real-world conditions:")
        print("  • J1: Fixed-time signals (45s EW / 35s NS)")
        print("  • J2: No traffic lights (real-world condition)")
        print("  • No AI optimization")
        print("  • Traditional traffic flow")
        print("-"*60)
        
        try:
            start_time = time.time()
            print("Launching baseline simulation...")
            # Use Popen for better GUI compatibility
            process = subprocess.Popen([
                sys.executable, 'baseline_traffic_controller.py'
            ], shell=True)
            
            # Wait for completion with timeout
            try:
                process.wait(timeout=1800)  # 30-minute timeout
                elapsed = time.time() - start_time
                if process.returncode == 0:
                    print(f"[SUCCESS] Baseline simulation completed in {elapsed/60:.1f} minutes")
                    self.simulation_status['baseline'] = True
                    return True
                else:
                    print(f"[ERROR] Baseline simulation failed with return code: {process.returncode}")
                    return False
            except subprocess.TimeoutExpired:
                print("[TIMEOUT] Baseline simulation timed out (30 minutes)")
                process.terminate()
                return False
                
        except Exception as e:
            print(f"[ERROR] Error running baseline simulation: {e}")
            return False
    
    def run_comparative_analysis(self):
        """Run the comparative analysis between optimized and baseline"""
        print("="*60)
        print("RUNNING COMPARATIVE ANALYSIS")
        print("="*60)
        print("Analyzing performance differences between scenarios...")
        print("Generating comparison metrics and visualizations...")
        print("-"*60)
        
        try:
            result = subprocess.run([
                sys.executable, 'comparative_analyzer.py'
            ], capture_output=True, text=True, timeout=300)  # 5-minute timeout
            
            if result.returncode == 0:
                print("[SUCCESS] Comparative analysis completed")
                print(result.stdout)
                self.simulation_status['comparison'] = True
                return True
            else:
                print(f"[ERROR] Comparative analysis failed:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] Comparative analysis timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Error running comparative analysis: {e}")
            return False
    
    def show_main_menu(self):
        """Display the main menu options"""
        print("="*80)
        print("ZAMBOANGA KCC TRAFFIC CONTROL COMPARISON SYSTEM")
        print("Optimized AI vs Real-World Baseline Analysis")
        print("="*80)
        print("")
        print("Available Options:")
        print("  1. [RUN ALL] Run Complete Comparison Study (All Simulations + Analysis)")
        print("  2. [AI] Run Optimized AI Simulation Only")
        print("  3. [BASELINE] Run Baseline Real-World Simulation Only")
        print("  4. [ANALYSIS] Run Comparative Analysis Only (requires existing data)")
        print("  5. [STATUS] Check Data Status")
        print("  6. [CLEAN] Clean Up Previous Results")
        print("  0. [EXIT] Exit")
        print("")
        
        # Show current status
        opt_status = "[OK]" if self.simulation_status['optimized'] else "[PENDING]"
        base_status = "[OK]" if self.simulation_status['baseline'] else "[PENDING]"
        comp_status = "[OK]" if self.simulation_status['comparison'] else "[PENDING]"
        
        print(f"Current Status:")
        print(f"  {opt_status} Optimized Data Available")
        print(f"  {base_status} Baseline Data Available")
        print(f"  {comp_status} Comparison Analysis Complete")
        print("="*80)
    
    def clean_previous_results(self):
        """Clean up previous simulation results"""
        print("Cleaning up previous results...")
        
        files_to_clean = [
            'traffic_metrics_500h.csv',
            'optimized_traffic_metrics.csv',
            'traffic_metrics.csv',
            'baseline_traffic_metrics.csv',
            'optimized_vs_baseline_comparison.png',
            'optimized_vs_baseline_report.txt'
        ]
        
        cleaned_files = []
        for file in files_to_clean:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    cleaned_files.append(file)
                except Exception as e:
                    print(f"  [WARNING] Could not remove {file}: {e}")
        
        if cleaned_files:
            print(f"  [OK] Cleaned {len(cleaned_files)} files:")
            for file in cleaned_files:
                print(f"    - {file}")
        else:
            print("  [INFO] No previous results found to clean")
        
        # Reset status
        self.simulation_status = {
            'optimized': False,
            'baseline': False,
            'comparison': False
        }
        print("")
    
    def run_complete_study(self):
        """Run the complete comparison study from start to finish"""
        print("="*80)
        print("RUNNING COMPLETE TRAFFIC CONTROL COMPARISON STUDY")
        print("="*80)
        print(f"Study started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Estimated total time: 30-40 minutes")
        print("")
        print("This will execute:")
        print("  1. Optimized AI Traffic Simulation (500 hours)")
        print("  2. Baseline Real-World Simulation (500 hours)")
        print("  3. Comparative Performance Analysis")
        print("  4. Generate Reports and Visualizations")
        print("")
        
        response = input("Continue with complete study? (y/N): ").strip().lower()
        if response != 'y':
            print("Study cancelled.")
            return
        
        total_start = time.time()
        
        # Step 1: Run optimized simulation
        if not self.simulation_status['optimized']:
            if not self.run_optimized_simulation():
                print("[ERROR] Complete study failed at optimized simulation")
                return
        else:
            print("[OK] Using existing optimized simulation data")
        
        print("")
        
        # Step 2: Run baseline simulation
        if not self.simulation_status['baseline']:
            if not self.run_baseline_simulation():
                print("[ERROR] Complete study failed at baseline simulation")
                return
        else:
            print("[OK] Using existing baseline simulation data")
        
        print("")
        
        # Step 3: Run comparative analysis
        if not self.run_comparative_analysis():
            print("[ERROR] Complete study failed at comparative analysis")
            return
        
        total_elapsed = time.time() - total_start
        
        print("="*80)
        print("COMPLETE TRAFFIC CONTROL COMPARISON STUDY FINISHED!")
        print("="*80)
        print(f"Total execution time: {total_elapsed/60:.1f} minutes")
        print(f"Study completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")
        print("Generated Files:")
        print("  > optimized_vs_baseline_comparison.png")
        print("  > optimized_vs_baseline_report.txt")
        print("  > traffic_metrics_500h.csv (optimized data)")
        print("  > baseline_traffic_metrics.csv (baseline data)")
        print("")
        print("Your thesis comparison data is ready for analysis!")
        print("="*80)
    
    def run(self):
        """Main execution loop"""
        if not self.check_requirements():
            return
        
        self.check_existing_data()
        
        while True:
            self.show_main_menu()
            
            choice = input("\nSelect option (0-6): ").strip()
            print("")
            
            if choice == '0':
                print("Exiting traffic control comparison system.")
                break
            elif choice == '1':
                self.run_complete_study()
            elif choice == '2':
                self.run_optimized_simulation()
            elif choice == '3':
                self.run_baseline_simulation()
            elif choice == '4':
                if not (self.simulation_status['optimized'] and self.simulation_status['baseline']):
                    print("[ERROR] Both optimized and baseline data required for comparison")
                    print("   Please run simulations first (options 1, 2, or 3)")
                else:
                    self.run_comparative_analysis()
            elif choice == '5':
                self.check_existing_data()
            elif choice == '6':
                confirm = input("WARNING: This will delete all previous results. Continue? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.clean_previous_results()
            else:
                print("[ERROR] Invalid option. Please select 0-6.")
            
            if choice != '0':
                input("\nPress Enter to continue...")

# Execute the integrated runner
if __name__ == "__main__":
    runner = IntegratedComparisonRunner()
    runner.run()