#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def plot_concurrent_results(csv_file='p2_results.csv', output_file='p2_plot.png'):
    """Plot the concurrent client experiment results"""
    
    try:
        # Read results
        df = pd.read_csv(csv_file)
        
        if df.empty:
            print(f"No data found in {csv_file}")
            return
        
        # Ensure 'num_clients' is integer
        df['num_clients'] = df['num_clients'].astype(int)
        
        # Sort by number of clients
        df = df.sort_values('num_clients')
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Plot mean completion time with error bars (95% confidence intervals)
        x = df['num_clients']
        y = df['mean_time']
        
        # Calculate error bars from confidence intervals
        lower_error = df['mean_time'] - df['ci_lower']
        upper_error = df['ci_upper'] - df['mean_time']
        
        plt.errorbar(x, y, yerr=[lower_error, upper_error], 
                     fmt='bo-', linewidth=2, markersize=8, capsize=5,
                     label='Average Completion Time per Client')
        
        # Customize the plot
        plt.xlabel('Number of Concurrent Clients', fontsize=14)
        plt.ylabel('Average Completion Time per Client (seconds)', fontsize=14)
        plt.title('Concurrent Word Counter Performance\n(Part 2: Sequential Server Processing)', fontsize=16)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=12)
        
        # Set x-axis ticks
        plt.xticks(x, fontsize=12)
        plt.yticks(fontsize=12)
        
        # Add some styling
        plt.tight_layout()
        
        # Add annotation with key observation
        max_clients = x.max()
        max_time = y.max()
        plt.annotate(
            'Completion time increases\nwith more clients due to\nsequential processing', 
            xy=(max_clients * 0.7, max_time * 0.8),
            fontsize=11, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7)
        )
        
        # Save the plot
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved as {output_file}")
        
        # Display statistics
        print("\nExperiment Summary:")
        print("=" * 50)
        for _, row in df.iterrows():
            print(f"Clients: {int(row['num_clients']):2d} | "
                  f"Mean Time: {row['mean_time']:.4f}s | "
                  f"95% CI: [{row['ci_lower']:.4f}, {row['ci_upper']:.4f}] | "
                  f"Samples: {row['num_samples']}")
        
        # Calculate scaling factor
        if len(df) >= 2:
            time_ratio = df.iloc[-1]['mean_time'] / df.iloc[0]['mean_time']
            client_ratio = df.iloc[-1]['num_clients'] / df.iloc[0]['num_clients']
            print(f"\nScaling Analysis:")
            print(f"Time increased by factor of {time_ratio:.2f}")
            print(f"Clients increased by factor of {client_ratio:.2f}")
            print(f"Time scaling efficiency: {client_ratio/time_ratio:.2f}")
        
        plt.show()
        
    except FileNotFoundError:
        print(f"Results file {csv_file} not found. Run experiments first.")
    except Exception as e:
        print(f"Error plotting results: {e}")

def main():
    csv_file = 'p2_results.csv'
    output_file = 'p2_plot.png'
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    plot_concurrent_results(csv_file, output_file)

if __name__ == "__main__":
    main()
