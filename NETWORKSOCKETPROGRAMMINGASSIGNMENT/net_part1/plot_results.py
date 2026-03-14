#!/usr/bin/env python3
"""
Enhanced plotting script for Part 1 results with detailed analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

def load_and_validate_data():
    """Load and validate experimental data"""
    results_file = Path("results.csv")
    
    if not results_file.exists():
        print("Error: results.csv not found. Run experiments first with 'make plot'")
        sys.exit(1)
    
    df = pd.read_csv(results_file)
    
    # Validate data structure
    required_columns = ['k', 'run', 'elapsed_ms']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: CSV must contain columns: {required_columns}")
        print(f"Found columns: {list(df.columns)}")
        sys.exit(1)
    
    if df.empty:
        print("Error: No data found in results.csv")
        sys.exit(1)
    
    print(f"Loaded {len(df)} data points")
    print(f"K values: {sorted(df['k'].unique())}")
    print(f"Runs per K: {df.groupby('k').size().values}")
    
    return df

def calculate_statistics(df):
    """Calculate mean, std, and confidence intervals"""
    stats = df.groupby("k")["elapsed_ms"].agg([
        'mean', 'std', 'count', 'min', 'max'
    ]).reset_index()
    
    # Calculate 95% confidence intervals
    # Using t-distribution for small samples (n=5)
    from scipy import stats as scipy_stats
    
    confidence_intervals = []
    for _, row in stats.iterrows():
        if row['count'] > 1:
            # t-distribution critical value for 95% CI
            t_critical = scipy_stats.t.ppf(0.975, row['count'] - 1)
            sem = row['std'] / np.sqrt(row['count'])
            ci = t_critical * sem
        else:
            ci = 0
        confidence_intervals.append(ci)
    
    stats['ci95'] = confidence_intervals
    
    return stats

def create_comprehensive_plot(stats):
    """Create comprehensive performance plot"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Main performance plot
    ax1.errorbar(stats['k'], stats['mean'], yerr=stats['ci95'], 
                fmt='o-', capsize=5, capthick=2, linewidth=2, markersize=8,
                color='#2E86C1', markerfacecolor='#3498DB', markeredgewidth=2)
    
    ax1.set_xlabel('k (words per request)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Completion time (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('TCP Word Counter Performance vs Batch Size\n(Mean ± 95% CI, n=5)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    
    # Add data labels
    for _, row in stats.iterrows():
        ax1.annotate(f'{row["mean"]:.1f}ms', 
                    (row['k'], row['mean']), 
                    textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9)
    
    # Throughput analysis (approximate)
    # Assume total words processed is roughly proportional to k
    stats['throughput_approx'] = stats['k'] / (stats['mean'] / 1000)  # words/second
    
    ax2.semilogx(stats['k'], stats['throughput_approx'], 'o-', 
                color='#E74C3C', linewidth=2, markersize=8)
    ax2.set_xlabel('k (words per request)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Throughput (words/second)', fontsize=12, fontweight='bold')
    ax2.set_title('Approximate Throughput vs Batch Size', 
                  fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("p1_plot.png", dpi=300, bbox_inches='tight')
    print("Saved comprehensive plot as p1_plot.png")
    
    return fig

def print_analysis_summary(df, stats):
    """Print detailed analysis summary"""
    print("\n" + "="*80)
    print("PART 1 ANALYSIS SUMMARY - MININET TCP PERFORMANCE")
    print("="*80)
    
    print(f"\nEXPERIMENTAL SETUP:")
    print(f"- Network: Mininet topology (2 hosts via switch)")
    print(f"- Protocol: TCP with connection per request batch")
    print(f"- Total data points: {len(df)}")
    print(f"- K values tested: {sorted(df['k'].unique())}")
    print(f"- Repetitions per k: {df.groupby('k').size().iloc[0]}")
    
    print(f"\nPERFORMANCE RESULTS:")
    print(f"{'K Value':<8} {'Mean (ms)':<12} {'Std Dev':<12} {'95% CI':<12} {'Min':<8} {'Max':<8}")
    print("-" * 68)
    
    for _, row in stats.iterrows():
        print(f"{row['k']:<8} {row['mean']:<12.2f} {row['std']:<12.2f} {row['ci95']:<12.2f} "
              f"{row['min']:<8.0f} {row['max']:<8.0f}")
    
    # Calculate performance improvements
    baseline = stats[stats['k'] == stats['k'].min()]['mean'].iloc[0]
    best = stats[stats['k'] == stats['k'].max()]['mean'].iloc[0]
    improvement = ((baseline - best) / baseline) * 100
    
    print(f"\nKEY INSIGHTS:")
    print(f"- Best performance: k={stats.loc[stats['mean'].idxmin(), 'k']} "
          f"({stats['mean'].min():.1f}ms)")
    print(f"- Worst performance: k={stats.loc[stats['mean'].idxmax(), 'k']} "
          f"({stats['mean'].max():.1f}ms)")
    print(f"- Overall improvement: {improvement:.1f}% from k=1 to k=max")
    
    # TCP connection analysis
    print(f"\nTCP CONNECTION OVERHEAD ANALYSIS:")
    k1_time = stats[stats['k'] == 1]['mean'].iloc[0] if 1 in stats['k'].values else None
    if k1_time:
        total_words = estimate_total_words()
        connections_k1 = total_words  # One connection per word with k=1
        overhead_per_conn = k1_time / connections_k1
        print(f"- Estimated words in dataset: ~{total_words}")
        print(f"- TCP connections with k=1: {connections_k1}")
        print(f"- Overhead per connection: ~{overhead_per_conn:.3f}ms")
    
    print(f"\nRECOMMENDations:")
    optimal_k = stats.loc[stats['mean'].idxmin(), 'k']
    print(f"- Optimal k value: {optimal_k}")
    print(f"- Use k≥10 for good performance (diminishing returns beyond k=50)")
    print(f"- TCP connection batching is critical for performance")
    
    print("="*80)

def estimate_total_words():
    """Estimate total words in the dataset"""
    words_file = Path("words.txt")
    if words_file.exists():
        content = words_file.read_text().strip()
        return len(content.split(','))
    return 489  # Default estimate

def main():
    print("Part 1 Results Analysis and Plotting")
    print("-" * 40)
    
    # Load and validate data
    df = load_and_validate_data()
    
    # Calculate statistics
    print("Calculating statistics...")
    stats = calculate_statistics(df)
    
    # Create plots
    print("Creating plots...")
    try:
        fig = create_comprehensive_plot(stats)
        plt.show()
    except ImportError as e:
        if "scipy" in str(e):
            print("Warning: scipy not available, using normal approximation for CI")
            # Fallback to normal approximation
            stats['ci95'] = 1.96 * stats['std'] / np.sqrt(stats['count'])
            fig = create_comprehensive_plot(stats)
            plt.show()
        else:
            raise
    
    # Print analysis summary
    print_analysis_summary(df, stats)
    
    # Save detailed results
    output_file = Path("detailed_results.txt")
    with output_file.open("w") as f:
        f.write("PART 1 DETAILED RESULTS\n")
        f.write("="*50 + "\n\n")
        f.write("Raw Data:\n")
        f.write(df.to_string(index=False))
        f.write("\n\nStatistical Summary:\n")
        f.write(stats.to_string(index=False))
    
    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)