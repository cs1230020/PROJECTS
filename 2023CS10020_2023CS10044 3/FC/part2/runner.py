#!/usr/bin/env python3
import subprocess
import json
import time
import csv
import os
import signal
import sys
import statistics
from datetime import datetime

def kill_server():
    """Kill any existing server process"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['pkill', '-f', 'server.py'], stderr=subprocess.DEVNULL)
        time.sleep(0.5)
    except:
        pass

def update_config(k_value):
    """Update config.json with new k value"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    config['k'] = k_value
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    return config

def run_single_experiment():
    """Run a single client experiment and return completion time"""
    start_time = time.time()
    
    try:
        # Run client and capture output
        result = subprocess.run(['python', 'client.py'], 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode != 0:
            print(f"Client error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Client timeout")
        return None
    except Exception as e:
        print(f"Error running client: {e}")
        return None
    
    end_time = time.time()
    completion_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    return completion_time

def calculate_confidence_interval(data, confidence=0.95):
    """Calculate mean and 95% confidence interval"""
    if len(data) < 2:
        return statistics.mean(data), 0
    
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    margin = 1.96 * (stdev / (len(data) ** 0.5))  # 95% CI
    
    return mean, margin

def run_experiments(k_values, num_repetitions):
    """Run experiments for different k values"""
    results = []
    
    # Kill any existing server
    kill_server()
    
    # Start server
    print("Starting server...")
    server_process = subprocess.Popen(['python', 'server.py'], 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.DEVNULL)
    time.sleep(2)  # Give server time to start
    
    try:
        if server_process.poll() is not None:
            print("Error: Server failed to start")
            return
        
        print(f"Running experiments with {num_repetitions} repetitions each...")
        print("-" * 60)
        
        for k in k_values:
            print(f"\nTesting k = {k}")
            
            config = update_config(k)
            
            times = []
            successful_runs = 0
            
            for rep in range(num_repetitions):
                print(f"  Repetition {rep + 1}/{num_repetitions}", end='')
                
                completion_time = run_single_experiment()
                
                if completion_time is not None:
                    times.append(completion_time)
                    successful_runs += 1
                    print(f" - {completion_time:.2f} ms")
                else:
                    print(" - Failed")
                
                time.sleep(0.1)
            
            if successful_runs > 0:
                avg_time, ci_margin = calculate_confidence_interval(times)
                
                print(f"  Average: {avg_time:.2f} ms")
                print(f"  95% CI: ±{ci_margin:.2f} ms")
                print(f"  Successful runs: {successful_runs}/{num_repetitions}")
                
                results.append({
                    'k': k,
                    'avg_time': avg_time,
                    'ci_margin': ci_margin,
                    'times': times,
                    'successful_runs': successful_runs
                })
            else:
                print(f"  All runs failed for k={k}")
        
        print("\n" + "-" * 60)
        
    except KeyboardInterrupt:
        print("\nExperiment interrupted by user")
    finally:
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()
        kill_server()
    
    return results

def save_results(results):
    """Save results to CSV file"""
    if not results:
        print("No results to save")
        return
    
    max_reps = max(len(r['times']) for r in results)
    
    with open('experiment_results.csv', 'w', newline='') as f:
        header = ['k', 'avg_time_ms', 'ci_margin', 'successful_runs']
        header.extend([f'rep{i+1}' for i in range(max_reps)])
        
        writer = csv.writer(f)
        writer.writerow(header)
        
        for result in results:
            row = [
                result['k'],
                f"{result['avg_time']:.2f}",
                f"{result['ci_margin']:.2f}",
                result['successful_runs']
            ]
            row.extend([f"{t:.2f}" for t in result['times']])
            row.extend([''] * (max_reps - len(result['times'])))
            
            writer.writerow(row)
    
    print(f"Results saved to experiment_results.csv")
    
    with open('results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['k', 'avg_time_ms', 'ci_margin'])
        
        for result in results:
            writer.writerow([
                result['k'],
                f"{result['avg_time']:.2f}",
                f"{result['ci_margin']:.2f}"
            ])
    
    print("Summary saved to results.csv")

def main():
    k_values = [1, 5, 10, 25, 50, 100, 200, 500]
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            num_repetitions = config.get('num_iterations', 5)
    except:
        num_repetitions = 5
    
    if len(sys.argv) > 1:
        k_values = [int(k) for k in sys.argv[1:]]
    
    print(f"Word Counter Client-Server Experiment")
    print(f"=====================================")
    print(f"K values to test: {k_values}")
    print(f"Repetitions per k: {num_repetitions}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not os.path.exists('server.py'):
        print("Error: server.py not found.")
        sys.exit(1)
    
    if not os.path.exists('client.py'):
        print("Error: client.py not found.")
        sys.exit(1)
    
    results = run_experiments(k_values, num_repetitions)
    
    if results:
        save_results(results)
        print(f"\nExperiment completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Run 'python plot_concurrent_results.py' to generate the plot")
    else:
        print("No successful experiments completed")

if __name__ == "__main__":
    main()
