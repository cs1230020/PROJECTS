#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def calculate_jfi(times):
    utilities = [1.0 / t for t in times if t > 0]
    if not utilities:
        return 0.0
    n = len(utilities)
    return (sum(utilities) ** 2) / (n * sum(u ** 2 for u in utilities))

def plot_results(csv_file="part3_results.csv", output_file="p3_plot.png"):
    if not os.path.exists(csv_file):
        print(f"No results file found: {csv_file}")
        return

    df = pd.read_csv(csv_file)
    if df.empty:
        print("No data to plot")
        return

    jfi_by_c = []
    for c_val, group in df.groupby("c"):
        times = group["completion_time"].tolist()
        jfi = calculate_jfi(times)
        jfi_by_c.append((c_val, jfi))

    jfi_by_c.sort(key=lambda x: x[0])
    c_values, jfi_values = zip(*jfi_by_c)

    plt.figure(figsize=(10, 6))
    plt.plot(c_values, jfi_values, marker="o")
    plt.title("Fairness vs Greediness (FCFS scheduling)")
    plt.xlabel("c (back-to-back requests by greedy client)")
    plt.ylabel("Jain’s Fairness Index")
    plt.grid(True)

    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"✅ Plot saved at {os.path.abspath(output_file)}")

if __name__ == "__main__":
    plot_results()
