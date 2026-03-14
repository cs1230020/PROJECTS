# analysis.py
import json
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import sys
from datetime import datetime

def calculate_jfi(completion_times):
    
    n = len(completion_times)
    if n == 0 or all(t == 0 for t in completion_times):
        return 0
    
    # Filter out any negative times (failed clients)
    valid_times = [t for t in completion_times if t > 0]
    if not valid_times:
        return 0
    
    sum_squared = sum(valid_times) ** 2
    sum_of_squares = sum(t**2 for t in valid_times)
    
    if sum_of_squares == 0:
        return 0
    
    jfi = sum_squared / (len(valid_times) * sum_of_squares)
    return jfi

def kill_existing_servers():
    
    try:
        subprocess.run(['pkill', '-f', 'python.*server.py'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        time.sleep(0.5)
    except:
        pass

def run_single_experiment(c_value, run_number, total_runs):
    
    print(f"    Run {run_number}/{total_runs}...", end='', flush=True)
    
    # Update config with current c value
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    config['c'] = c_value
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Kill any existing servers
    kill_existing_servers()
    
    # Start server
    server_process = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Run client
        result = subprocess.run(
            [sys.executable, 'client.py'],
            capture_output=True,
            text=True,
            timeout=120  # Increased timeout
        )
        
        if result.returncode != 0:
            print(f" Failed (return code: {result.returncode})")
            return None
        
        # Try to load results from the saved JSON file
        results_file = f"results_c{c_value}.json"
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
            
            # Extract completion times
            completion_times = []
            normal_times = []
            greedy_times = []
            
            for r in results:
                if r['completion_time'] > 0:
                    completion_times.append(r['completion_time'])
                    if r['type'] == 'normal':
                        normal_times.append(r['completion_time'])
                    else:
                        greedy_times.append(r['completion_time'])
            
            if len(completion_times) == 10:  # Should have 10 clients
                jfi = calculate_jfi(completion_times)
                
                avg_normal = np.mean(normal_times) if normal_times else 0
                avg_greedy = greedy_times[0] if greedy_times else 0
                
                print(f" JFI={jfi:.3f} (Normal avg: {avg_normal:.2f}s, Greedy: {avg_greedy:.2f}s)")
                
                # Clean up results file
                os.remove(results_file)
                
                return {
                    'completion_times': completion_times,
                    'normal_times': normal_times,
                    'greedy_times': greedy_times,
                    'jfi': jfi
                }
            else:
                print(f" Failed (only {len(completion_times)} clients completed)")
                if os.path.exists(results_file):
                    os.remove(results_file)
                return None
        else:
            print(f" Failed (no results file generated)")
            return None
    
    except subprocess.TimeoutExpired:
        print(" Timeout!")
        return None
    except Exception as e:
        print(f" Error: {e}")
        return None
    finally:
        # Kill server
        server_process.terminate()
        try:
            server_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            server_process.kill()
        time.sleep(0.5)

def save_raw_data(all_results):
    """Save raw experimental data for future reference"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"part3_raw_data_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nRaw data saved to {filename}")
    return filename

def plot_results():
    """Run experiments and plot results"""
    print("Part 3: FCFS Scheduling Analysis")
    print("=" * 60)
    
    c_values = list(range(1, 11))
    num_repetitions = 1
    
    all_results = {}
    all_jfis_mean = []
    all_jfis_std = []
    all_errors = []
    
    # Additional tracking for detailed analysis
    normal_avg_times = []
    greedy_avg_times = []
    
    for c in c_values:
        print(f"\nTesting c={c} (greedy client sends {c} parallel requests)")
        
        jfis = []
        normal_times_all = []
        greedy_times_all = []
        valid_runs = 0
        
        for rep in range(1, num_repetitions + 1):
            result = run_single_experiment(c, rep, num_repetitions)
            
            if result and result['jfi'] is not None:
                jfis.append(result['jfi'])
                normal_times_all.extend(result['normal_times'])
                greedy_times_all.extend(result['greedy_times'])
                valid_runs += 1
        
        if valid_runs > 0:
            mean_jfi = np.mean(jfis)
            std_jfi = np.std(jfis) if len(jfis) > 1 else 0
            
            # 95% confidence interval
            if valid_runs > 1:
                error = 1.96 * std_jfi / np.sqrt(valid_runs)
            else:
                error = 0
            
            all_jfis_mean.append(mean_jfi)
            all_jfis_std.append(std_jfi)
            all_errors.append(error)
            
            # Calculate average times
            avg_normal = np.mean(normal_times_all) if normal_times_all else 0
            avg_greedy = np.mean(greedy_times_all) if greedy_times_all else 0
            normal_avg_times.append(avg_normal)
            greedy_avg_times.append(avg_greedy)
            
            all_results[c] = {
                'jfis': jfis,
                'mean': mean_jfi,
                'std': std_jfi,
                'error': error,
                'valid_runs': valid_runs,
                'avg_normal_time': avg_normal,
                'avg_greedy_time': avg_greedy
            }
            
            print(f"  Summary: mean JFI = {mean_jfi:.3f} ± {error:.3f} ({valid_runs}/{num_repetitions} successful runs)")
        else:
            print(f"  Failed: No valid runs completed")
            # Add placeholder values
            all_jfis_mean.append(0)
            all_jfis_std.append(0)
            all_errors.append(0)
            normal_avg_times.append(0)
            greedy_avg_times.append(0)
    
    # Save raw data
    raw_data_file = save_raw_data(all_results)
    
    # Create plot
    create_plot(c_values, all_jfis_mean, all_errors, normal_avg_times, greedy_avg_times)
    
    # Print summary
    print_summary(all_results, raw_data_file)

def create_plot(c_values, all_jfis_mean, all_errors, normal_avg_times, greedy_avg_times):
    """Create the JFI vs c plot"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: JFI vs c
    ax1.errorbar(c_values, all_jfis_mean, yerr=all_errors, 
                 marker='o', markersize=8, capsize=5, 
                 linewidth=2, elinewidth=2, capthick=2,
                 color='darkblue', ecolor='gray',
                 label='Mean JFI with 95% CI')
    
    ax1.set_xlabel('Number of parallel requests by greedy client (c)', fontsize=12)
    ax1.set_ylabel('Jain Fairness Index (JFI)', fontsize=12)
    ax1.set_title('Impact of Greedy Client on Fairness (FCFS)', fontsize=14)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylim(0, 1.1)
    ax1.set_xlim(0.5, 10.5)
    
    # Add reference lines
    ax1.axhline(y=1, color='green', linestyle=':', alpha=0.5, label='Perfect fairness')
    ax1.axhline(y=0.5, color='orange', linestyle=':', alpha=0.5, label='Poor fairness')
    ax1.axhline(y=0.1, color='red', linestyle=':', alpha=0.5, label='Very poor fairness')
    ax1.legend(loc='best')
    
    # Plot 2: Completion times
    ax2.plot(c_values, normal_avg_times, 'b-o', label='Normal clients (avg)', linewidth=2)
    ax2.plot(c_values, greedy_avg_times, 'r-s', label='Greedy client', linewidth=2)
    ax2.set_xlabel('Number of parallel requests (c)', fontsize=12)
    ax2.set_ylabel('Average Completion Time (seconds)', fontsize=12)
    ax2.set_title('Completion Times: Normal vs Greedy', fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.suptitle('FCFS Scheduling Analysis - Part 3', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig('p3_plot.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved as p3_plot.png")

def print_summary(all_results, raw_data_file):
    """Print summary of analysis"""
    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)
    
    print("\nKey Observations:")
    
    # Find JFI at c=1 and c=10
    jfi_c1 = all_results.get(1, {}).get('mean', 0)
    jfi_c10 = all_results.get(10, {}).get('mean', 0)
    
    if jfi_c1 > 0 and jfi_c10 > 0:
        print(f"1. JFI changed from {jfi_c1:.3f} (c=1) to {jfi_c10:.3f} (c=10)")
        if jfi_c1 > jfi_c10:
            print(f"   - This represents a {(1-jfi_c10/jfi_c1)*100:.1f}% decrease in fairness")
    
    # Find when greedy client gets significant advantage
    greedy_advantage_c = None
    for c, data in all_results.items():
        if data.get('avg_normal_time', 0) > 0 and data.get('avg_greedy_time', 0) > 0:
            ratio = data['avg_greedy_time'] / data['avg_normal_time']
            if ratio < 0.8:  # Greedy is 20% faster
                greedy_advantage_c = c
                break
    
    if greedy_advantage_c:
        print(f"2. Greedy client gains significant advantage starting at c={greedy_advantage_c}")
        data = all_results[greedy_advantage_c]
        ratio = data['avg_greedy_time'] / data['avg_normal_time']
        print(f"   - Greedy client is {(1-ratio)*100:.1f}% faster than normal clients")
    
    # Find critical JFI threshold
    critical_c = None
    for c, data in all_results.items():
        if data.get('mean', 0) < 0.5:  # JFI below 0.5 indicates poor fairness
            critical_c = c
            break
    
    if critical_c:
        print(f"3. JFI drops below 0.5 (poor fairness) at c={critical_c}")
    
    print(f"\n4. Raw experimental data saved to: {raw_data_file}")
    
    print("\nConclusion:")
    print("  - FCFS scheduling is vulnerable to greedy clients")
    print("  - As c increases, the greedy client monopolizes server resources")
    print("  - This leads to longer wait times for normal clients and decreased fairness")
    print("  - Round-robin scheduling (Part 4) should address these fairness issues")
    
    print("\nExpected behavior if c increased further:")
    print("  - JFI would approach 1/n (0.1 for 10 clients) as the greedy client")
    print("    increasingly dominates server time")
    print("  - Normal clients would experience severe starvation")
    print("  - System would become effectively single-client")

def main():
    """Main function to run the analysis"""
    # Check if required files exist
    required_files = ['server.py', 'client.py', 'config.json', 'words.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Error: Missing required files: {', '.join(missing_files)}")
        print("Please ensure all required files are in the current directory.")
        sys.exit(1)
    
    # Check if we're in the correct directory (part3)
    current_dir = os.path.basename(os.getcwd())
    if current_dir != 'part3':
        print("Warning: This script should be run from the 'part3' directory")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Load and validate config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Ensure required fields exist
        required_fields = ['server_ip', 'server_port', 'k', 'filename', 'num_clients']
        missing_fields = [f for f in required_fields if f not in config]
        
        if missing_fields:
            print(f"Error: Missing fields in config.json: {', '.join(missing_fields)}")
            sys.exit(1)
        
        # Set default values if not present
        if 'num_repetitions' not in config:
            config['num_repetitions'] = 5
            print("Note: Using default num_repetitions = 5")
        
        if 'c' not in config:
            config['c'] = 1
            print("Note: Using default c = 1 (will be varied during analysis)")
        
        # Ensure num_clients is 10 for this experiment
        if config['num_clients'] != 10:
            print(f"Warning: Changing num_clients from {config['num_clients']} to 10 for Part 3 analysis")
            config['num_clients'] = 10
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        sys.exit(1)
    
    # Kill any existing servers before starting
    print("Cleaning up any existing server processes...")
    kill_existing_servers()
    
    # Run the analysis
    try:
        plot_results()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        kill_existing_servers()
        sys.exit(1)
    except Exception as e:
        print(f"\nError during analysis: {e}")
        kill_existing_servers()
        sys.exit(1)
    
    # Final cleanup
    kill_existing_servers()
    
    print("\n" + "="*60)
    print("Part 3 analysis complete!")
    print("Check p3_plot.png for the results visualization")
    print("="*60)

if __name__ == "__main__":
    main()