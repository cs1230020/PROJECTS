#!/usr/bin/env python3

import json
import os
import time
import glob
import csv

class Runner:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        self.server_ip = self.config['server_ip']
        self.port = self.config['port']
        self.num_clients = self.config['num_clients']
        self.c = self.config['c']
        self.p = self.config['p']
        self.k = self.config['k']

        print(f"Config: {self.num_clients} clients, c={self.c}, p={self.p}, k={self.k}, server_ip={self.server_ip}, port={self.port}")

        self.results_csv = "part3_results.csv"
        with open(self.results_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["c", "client_id", "completion_time"])

    def cleanup_logs(self):
        logs = glob.glob("logs/*.log")
        for log in logs:
            os.remove(log)
        print("Cleaned old logs")

    def parse_logs(self):
        results = {"rogue": [], "normal": []}
        for logfile in glob.glob("logs/*.log"):
            with open(logfile, "r") as f:
                for line in f:
                    client_id, t = line.strip().split(",")
                    t = float(t)
                    if client_id.startswith("rogue"):
                        results["rogue"].append(t)
                    else:
                        results["normal"].append(t)
        return results

    def calculate_jfi(self, times):
        utilities = [1.0 / t for t in times if t > 0]
        if not utilities:
            return 0.0
        n = len(utilities)
        return (sum(utilities) ** 2) / (n * sum(u ** 2 for u in utilities))

    def run_experiment(self, c_value):
        print(f"Running experiment with c={c_value}")
        self.cleanup_logs()

        from topology import create_network
        net = create_network()

        try:
            server = net.get('server')
            clients = [net.get(f'client{i+1}') for i in range(self.num_clients)]

            print("Starting server...")
            server_proc = server.popen(f"python3 server.py --ip {self.server_ip} --port {self.port}")
            time.sleep(3)

            print("Starting clients...")
            rogue_proc = clients[0].popen(
                f"python3 client.py --batch-size {c_value} --client-id rogue "
                f"--server-ip {self.server_ip} --port {self.port}"
            )
            normal_procs = []
            for i in range(1, self.num_clients):
                proc = clients[i].popen(
                    f"python3 client.py --batch-size 1 --client-id normal_{i+1} "
                    f"--server-ip {self.server_ip} --port {self.port}"
                )
                normal_procs.append(proc)

            rogue_proc.wait()
            for proc in normal_procs:
                proc.wait()

            server_proc.terminate()
            server_proc.wait()
            time.sleep(1)

            results = self.parse_logs()

            with open(self.results_csv, "a", newline="") as f:
                writer = csv.writer(f)
                for t in results["rogue"]:
                    writer.writerow([c_value, "rogue", t])
                for t in results["normal"]:
                    writer.writerow([c_value, "normal", t])

            all_times = results["rogue"] + results["normal"]
            jfi = self.calculate_jfi(all_times)
            print(f"✅ JFI for c={c_value}: {jfi:.3f}")

        finally:
            net.stop()

    def run_varying_c(self):
        c_values = list(range(self.c, 21, 2))
        print("Running experiments with varying c values...")
        for c in c_values:
            print(f"\n--- Testing c = {c} ---")
            self.run_experiment(c)
        print("All experiments completed and saved to part3_results.csv")

def main():
    runner = Runner()
    runner.run_varying_c()

if __name__ == '__main__':
    main()
