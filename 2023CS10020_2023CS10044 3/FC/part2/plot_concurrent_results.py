import matplotlib.pyplot as plt
import csv

clients = []
avg_times = []
stdevs = []

with open("p2_results.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        clients.append(int(row["num_clients"]))
        avg_times.append(float(row["avg_time"]))
        stdevs.append(float(row["stdev"]))

plt.errorbar(clients, avg_times, yerr=stdevs, fmt='-o', capsize=5)
plt.xlabel("Number of Clients")
plt.ylabel("Average Completion Time (seconds)")
plt.title("Concurrent Word Counter: Completion Time per Client")
plt.grid(True)

# Save before showing
plt.savefig("p2_plot.png")

# Optional: also display interactively
# plt.show()