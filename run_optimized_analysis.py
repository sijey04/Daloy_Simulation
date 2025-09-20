# =============================================================================
#           INTEGRATED OPTIMIZED TRAFFIC ANALYSIS RUNNER
#           Runs the optimized controller and analyzes results automatically
# =============================================================================

import os
import sys
import subprocess
import time
from datetime import datetime

def run_optimized_simulation_with_analysis():
    """Run the optimized traffic controller and then analyze the results"""
    
    print("="*80)
    print("🚦 INTEGRATED OPTIMIZED TRAFFIC SIMULATION & ANALYSIS")
    print("="*80)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 This will run the 500-hour optimized simulation and analyze results")
    print("⏱️  Note: Full simulation may take significant time depending on hardware")
    print("="*80)
    
    # Check if required files exist
    required_files = [
        'optimized_traffic_controller.py',
        'traffic_analyzer.py',
        'KCCIntersection.sumocfg',
        'KCCIntersection_500h.rou.xml'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   • {file}")
        print("\nPlease ensure all files are present before running.")
        return False
    
    print("✅ All required files found")
    
    # Ask user for confirmation
    response = input("\n🤔 Do you want to run the full 500-hour simulation? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("📊 Running analysis on existing data instead...")
        run_analysis_only()
        return True
    
    print("\n" + "="*80)
    print("🚀 STARTING OPTIMIZED TRAFFIC SIMULATION")
    print("="*80)
    
    # Run the optimized traffic controller
    start_time = time.time()
    
    try:
        print("🔄 Running optimized traffic controller...")
        result = subprocess.run([sys.executable, 'optimized_traffic_controller.py'], 
                               capture_output=True, text=True, timeout=None)
        
        if result.returncode == 0:
            print("✅ Simulation completed successfully!")
            simulation_time = time.time() - start_time
            print(f"⏱️  Simulation took: {simulation_time/60:.1f} minutes")
        else:
            print("❌ Simulation encountered errors:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Simulation timed out")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running simulation: {e}")
        return False
    
    # Wait a moment for files to be written
    print("⏳ Waiting for data files to be written...")
    time.sleep(2)
    
    # Run the analysis
    print("\n" + "="*80)
    print("📊 STARTING TRAFFIC ANALYSIS")
    print("="*80)
    
    run_analysis_only()
    
    total_time = time.time() - start_time
    print(f"\n🎉 COMPLETE! Total time: {total_time/60:.1f} minutes")
    
    return True

def run_analysis_only():
    """Run only the traffic analysis on existing data"""
    
    try:
        print("🔄 Running traffic analysis...")
        result = subprocess.run([sys.executable, 'traffic_analyzer.py'], 
                               capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Analysis completed successfully!")
        else:
            print("⚠️ Analysis completed with warnings")
            
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        return False
    
    # Check for generated files
    expected_files = [
        'optimized_traffic_analysis_500h.png',
        'intersection_comparison_500h.png', 
        'optimized_traffic_report_500h.txt'
    ]
    
    print("\n📁 Checking for generated files:")
    for file in expected_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            # Try alternative names
            alt_file = file.replace('_500h', '_extended')
            if os.path.exists(alt_file):
                print(f"   ✅ {alt_file}")
            else:
                print(f"   ❌ {file} (not found)")
    
    return True

def quick_data_check():
    """Quick check of available data files"""
    print("\n📋 DATA FILE SUMMARY:")
    print("-" * 40)
    
    data_files = [
        ('traffic_metrics_500h.csv', '500-hour simulation data'),
        ('optimized_traffic_metrics.csv', 'Optimized simulation data'),
        ('traffic_metrics.csv', 'Legacy simulation data')
    ]
    
    found_data = False
    for filename, description in data_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} ({size:,} bytes) - {description}")
            found_data = True
        else:
            print(f"❌ {filename} - {description}")
    
    if not found_data:
        print("\n⚠️  No data files found. Run the simulation first!")
        return False
    
    return True

if __name__ == "__main__":
    print("🚦 Optimized Traffic Analysis Tool")
    print("Choose an option:")
    print("1. Run full simulation + analysis")
    print("2. Analyze existing data only") 
    print("3. Check available data files")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                run_optimized_simulation_with_analysis()
                break
            elif choice == '2':
                if quick_data_check():
                    run_analysis_only()
                break
            elif choice == '3':
                quick_data_check()
                break
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break