#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def plot_results(csv_file='results/part4_results.csv', output_file='p4_plot.png'):
    df = pd.read_csv(csv_file)
    c_values = df['c_value'].tolist()
    jfi_values = df['jfi'].tolist()

    plt.figure(figsize=(10,6))
    plt.plot(c_values, jfi_values, 'bo-', linewidth=2, markersize=8, label='Round-Robin Server')
    plt.xlabel('c (Rogue Client Batch Size)')
    plt.ylabel('Jain\'s Fairness Index (JFI)')
    plt.title('Fairness Analysis with Round-Robin Scheduling')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Perfect Fairness')
    for c, jfi in zip(c_values, jfi_values):
        plt.annotate(f'{jfi:.3f}', (c, jfi), xytext=(0,10), textcoords='offset points', ha='center', fontsize=9)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.show()
    print(f"Plot saved as {output_file}")

if __name__ == '__main__':
    plot_results()
