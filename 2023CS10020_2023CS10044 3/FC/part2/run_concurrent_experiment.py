import json
import subprocess
import statistics
import time

NUM_CLIENTS_LIST = [1, 4, 8, 12, 16, 20, 24, 28, 32]

with open("config.json") as f:
    config = json.load(f)

num_repetitions = config["num_iterations"]

results = {}

for nc in NUM_CLIENTS_LIST:
    config["num_clients"] = nc
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    times = []
    for r in range(num_repetitions):
        print(f"\n[Experiment] Running with {nc} clients (iteration {r+1})")
        server = subprocess.Popen(["python", "server.py"])
        time.sleep(1)  # Allow server to start

        output = subprocess.check_output(["python", "client.py"], text=True)
        server.kill()

        # Parse completion time from client output
        for line in output.splitlines():
            if "[RESULT]" in line:
                avg_time = float(line.split("=")[-1].strip().split()[0])
                times.append(avg_time)

    avg = statistics.mean(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0
    results[nc] = (avg, stdev)
    print(f"[Summary] Clients={nc}, Avg={avg:.4f}, Stdev={stdev:.4f}")

# Save results
with open("p2_results.csv", "w") as f:
    f.write("num_clients,avg_time,stdev\n")
    for nc, (avg, stdev) in results.items():
        f.write(f"{nc},{avg},{stdev}\n")

print("\n[Done] Results saved to p2_results.csv")
