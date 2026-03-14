#!/usr/bin/env python3
import json
import subprocess
import time
import csv
import statistics
import sys
import os

class ExperimentRunner:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.num_repetitions = self.config.get("num_repetitions", 3)
        self.results_file = "p2_results.csv"

    def run_single_experiment(self, args):
        """Run a single experiment with given parameters"""
        n_clients, repetition = args

        try:
            # Update config for this experiment
            temp_config = self.config.copy()
            temp_config["num_clients"] = n_clients

            with open("temp_config.json", "w") as f:
                json.dump(temp_config, f, indent=2)

            # Run the Mininet experiment script
            cmd = ["sudo", "python3", "topology.py", str(n_clients)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            completion_times = []

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")

                for line in lines:
                    # Old format: "clientX: Y.ZZZ seconds"
                    if "client" in line and "seconds" in line:
                        try:
                            time_str = line.split(": ")[1].split(" ")[0]
                            completion_times.append(float(time_str))
                        except (IndexError, ValueError):
                            continue

                    # New format: "ELAPSED_MS:123"
                    elif line.startswith("ELAPSED_MS:"):
                        try:
                            ms = int(line.split(":", 1)[1])
                            completion_times.append(ms / 1000.0)  # ms → sec
                        except ValueError:
                            continue

                if completion_times:
                    avg_time = statistics.mean(completion_times)
                    return (n_clients, repetition, avg_time, completion_times)
                else:
                    print(f"No completion times found for {n_clients} clients, rep {repetition}")
                    print("STDOUT:\n", result.stdout)
                    print("STDERR:\n", result.stderr)
                    return None
            else:
                print(f"Error running experiment with {n_clients} clients, rep {repetition}")
                print("STDOUT:\n", result.stdout)
                print("STDERR:\n", result.stderr)
                return None

        except subprocess.TimeoutExpired:
            print(f"Experiment timed out for {n_clients} clients, rep {repetition}")
            return None
        except Exception as e:
            print(f"Exception in experiment with {n_clients} clients, rep {repetition}: {e}")
            return None
        finally:
            if os.path.exists("temp_config.json"):
                os.remove("temp_config.json")

    def run_all_experiments(self):
        """Run experiments for different numbers of clients"""
        print("Starting Part 2 experiments...")
        print("Using topology: h1 = server, h2–hN = clients")

        client_counts = [1, 4, 8, 12, 16, 20, 24, 28, 32]

        all_experiments = []
        for n_clients in client_counts:
            for rep in range(self.num_repetitions):
                all_experiments.append((n_clients, rep))

        print(f"Running {len(all_experiments)} total experiments...")

        results = []
        for i, args in enumerate(all_experiments):
            print(f"\nExperiment {i+1}/{len(all_experiments)}: {args[0]} clients (rep {args[1]})")
            result = self.run_single_experiment(args)
            if result:
                results.append(result)
            time.sleep(3)

        if results:
            self.process_results(results, client_counts)
        else:
            print("No successful experiments completed!")
        return results

    def process_results(self, results, client_counts):
        """Process and save results"""
        print("Processing results...")

        grouped_results = {}
        for n_clients, rep, avg_time, completion_times in results:
            grouped_results.setdefault(n_clients, []).append(avg_time)

        final_results = []
        for n_clients in client_counts:
            if n_clients in grouped_results:
                times = grouped_results[n_clients]
                mean_time = statistics.mean(times)
                std_time = statistics.stdev(times) if len(times) > 1 else 0
                n = len(times)
                t_value = 2.776 if n == 5 else 2.0
                margin_error = t_value * (std_time / (n ** 0.5)) if n > 1 else 0
                ci_lower = mean_time - margin_error
                ci_upper = mean_time + margin_error

                final_results.append({
                    "num_clients": n_clients,
                    "mean_time": mean_time,
                    "std_time": std_time,
                    "ci_lower": ci_lower,
                    "ci_upper": ci_upper,
                    "num_samples": n,
                })

                print(f"Clients: {n_clients:2d}, Mean: {mean_time:.4f}s, "
                      f"Std: {std_time:.4f}s, CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

        with open(self.results_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "num_clients", "mean_time", "std_time", "ci_lower", "ci_upper", "num_samples"
            ])
            writer.writeheader()
            writer.writerows(final_results)

        print(f"Results saved to {self.results_file}")
        return final_results

def main():
    if os.geteuid() != 0:
        print("This script needs sudo (Mininet)")
        sys.exit(1)

    runner = ExperimentRunner()
    runner.run_all_experiments()

if __name__ == "__main__":
    main()
