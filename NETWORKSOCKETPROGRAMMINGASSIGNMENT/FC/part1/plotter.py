#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def plot_results():
    """Generate plot from experiment results"""
    
    # Check if results file exists
    if not os.path.exists('results.csv'):
        print("Error: results.csv not found. Run experiments first with 'python3 runner.py'")
        sys.exit(1)
    
    # Read results
    try:
        df = pd.read_csv('results.csv')
    except Exception as e:
        print(f"Error reading results.csv: {e}")
        sys.exit(1)
    
    # Extract data
    k_values = df['k'].values
    avg_times = df['avg_time_ms'].values
    ci_margins = df['ci_margin'].values
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Plot with error bars
    plt.errorbar(k_values, avg_times, yerr=ci_margins,
                 marker='o', markersize=8, 
                 capsize=5, capthick=2, 
                 linewidth=2, 
                 color='blue', 
                 ecolor='red',
                 label='Average completion time')
    
    # Customize plot
    plt.xlabel('k (Number of words per request)', fontsize=12)
    plt.ylabel('Average Completion Time (ms)', fontsize=12)
    plt.title('TCP Word Counter: Completion Time vs. Words per Request', fontsize=14)
    
    # Use log scale if range is large
    if max(k_values) / min(k_values) > 100:
        plt.xscale('log')
        plt.xlabel('k (Number of words per request) - Log Scale', fontsize=12)
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add legend
    plt.legend(loc='best')
    
    # Tight layout
    plt.tight_layout()
    
    # Save plot
    plt.savefig('p1_plot.png', dpi=300, bbox_inches='tight')
    print("Plot saved as p1_plot.png")
    
    # Also save a PDF version
    plt.savefig('p1_plot.pdf', format='pdf', bbox_inches='tight')
    print("Plot also saved as p1_plot.pdf")
    
    # Display plot statistics
    print("\nPlot Statistics:")
    print(f"Number of data points: {len(k_values)}")
    print(f"K range: {min(k_values)} to {max(k_values)}")
    print(f"Time range: {min(avg_times):.2f} to {max(avg_times):.2f} ms")
    
    # Find optimal k (minimum completion time)
    min_idx = np.argmin(avg_times)
    print(f"\nOptimal k value: {k_values[min_idx]} (completion time: {avg_times[min_idx]:.2f} ms)")
    
    # Create additional analysis plot
    create_analysis_plot(df)

def create_analysis_plot(df):
    """Create additional analysis plots"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # Plot 1: Completion time with confidence intervals
    k_values = df['k'].values
    avg_times = df['avg_time_ms'].values
    ci_margins = df['ci_margin'].values
    
    # Calculate upper and lower bounds
    lower_bound = avg_times - ci_margins
    upper_bound = avg_times + ci_margins
    
    ax1.plot(k_values, avg_times, 'b-', linewidth=2, label='Average')
    ax1.fill_between(k_values, lower_bound, upper_bound, 
                     alpha=0.3, color='blue', label='95% Confidence Interval')
    ax1.set_xlabel('k (Number of words per request)', fontsize=12)
    ax1.set_ylabel('Completion Time (ms)', fontsize=12)
    ax1.set_title('Completion Time with Confidence Intervals', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    if max(k_values) / min(k_values) > 100:
        ax1.set_xscale('log')
    
    # Plot 2: Throughput analysis
    # Calculate throughput (words per second)
    throughput = (k_values * 1000.0) / avg_times  # words per second
    
    ax2.plot(k_values, throughput, 'g-', linewidth=2, marker='o', markersize=6)
    ax2.set_xlabel('k (Number of words per request)', fontsize=12)
    ax2.set_ylabel('Throughput (words/second)', fontsize=12)
    ax2.set_title('Throughput vs. Request Size', fontsize=14)
    ax2.grid(True, alpha=0.3)
    
    if max(k_values) / min(k_values) > 100:
        ax2.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('p1_analysis.png', dpi=300, bbox_inches='tight')
    print("Additional analysis saved as p1_analysis.png")

def create_summary_table():
    """Create a summary table of results"""
    
    df = pd.read_csv('results.csv')
    
    # Create summary
    summary = []
    for _, row in df.iterrows():
        k = row['k']
        avg_time = row['avg_time_ms']
        ci_margin = row['ci_margin']
        throughput = (k * 1000.0) / avg_time
        
        summary.append({
            'k': k,
            'Avg Time (ms)': f"{avg_time:.2f}",
            '95% CI': f"±{ci_margin:.2f}",
            'Throughput (words/s)': f"{throughput:.2f}"
        })
    
    # Convert to DataFrame and save
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv('summary_table.csv', index=False)
    print("\nSummary table saved as summary_table.csv")
    
    # Print summary
    print("\nResults Summary:")
    print("-" * 70)
    print(summary_df.to_string(index=False))

def main():
    print("Generating plots for Part 1...")
    print("-" * 50)
    
    try:
        # Generate main plot
        plot_results()
        
        # Create summary table
        create_summary_table()
        
        print("\nPlotting completed successfully!")
        print("\nFiles generated:")
        print("  - p1_plot.png: Main results plot")
        print("  - p1_plot.pdf: PDF version of main plot")
        print("  - p1_analysis.png: Additional analysis plots")
        print("  - summary_table.csv: Summary of results")
        
    except Exception as e:
        print(f"Error during plotting: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()