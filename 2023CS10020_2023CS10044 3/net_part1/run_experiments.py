#!/usr/bin/env python3
# run_experiments.py
# Run inside host with Mininet (script checks for root)

import re
import time
import csv
import json
import sys
from pathlib import Path
from topo_wordcount import make_net

K_VALUES = [1, 2, 5, 10, 20, 50, 100]
RUNS_PER_K = 5
SERVER_CMD = "./server --config config.json"
CLIENT_CMD_BASE = "./client --config config.json --quiet"
RESULTS_CSV = Path("results.csv")

def modify_config(key, value):
    cfg = Path("config.json")
    if not cfg.exists():
        raise FileNotFoundError("config.json not found")
    with cfg.open("r") as f:
        config = json.load(f)
    config[key] = value
    with cfg.open("w") as f:
        json.dump(config, f, indent=2)

def ensure_files_exist():
    if not Path("words.txt").exists():
        print("Creating sample words.txt...")
        sample = "apple,banana,cherry,date,elderberry,fig,grape,honeydew,kiwi,lemon,mango,nectarine,orange,papaya,quince,raspberry,strawberry,tangerine,ugli,vanilla,watermelon\n"
        Path("words.txt").write_text(sample)
    if not Path("config.json").exists():
        print("Creating default config.json...")
        default = {
            "server_ip": "10.0.0.2",
            "server_port": 5000,
            "k": 5,
            "p": 0,
            "filename": "words.txt",
            "num_iterations": 5
        }
        with Path("config.json").open("w") as f:
            json.dump(default, f, indent=2)

def run_single_experiment(net, k_value, run_number):
    h1 = net.get('h1')  # client
    h2 = net.get('h2')  # server

    # Update config BEFORE starting server
    modify_config("k", k_value)

    # Start server on host h2 (redirect logs)
    server_log = f"/tmp/server_k{k_value}_run{run_number}.log"
    server_err = f"/tmp/server_k{k_value}_run{run_number}.err"
    print(f"Starting server for k={k_value}, run={run_number}")
    srv = h2.popen(SERVER_CMD, shell=True,
                  stdout=open(server_log, "w"),
                  stderr=open(server_err, "w"))
    time.sleep(0.8)  # allow bind

    try:
        client_cmd = f"{CLIENT_CMD_BASE} --k {k_value}"
        print(f"Running client on h1: {client_cmd}")
        output = h1.cmd(client_cmd)
        print(f"Client output preview: {output[:200]}")

        match = re.search(r"ELAPSED_MS:(\d+)", output)
        if not match:
            print(f"Warning: No ELAPSED_MS found for k={k_value} run={run_number}")
            print("Client output (full):")
            print(output)
            print(f"Check server logs: {server_log} and {server_err}")
            return None

        elapsed_ms = int(match.group(1))
        print(f"k={k_value}, run={run_number}: {elapsed_ms}ms")
        return elapsed_ms

    finally:
        try:
            srv.terminate()
            srv.wait(timeout=2)
        except Exception:
            try:
                srv.kill()
            except Exception:
                pass
        time.sleep(0.2)

def main():
    if Path(RESULTS_CSV).exists():
        backup = RESULTS_CSV.with_suffix(".backup.csv")
        print(f"Backing up existing {RESULTS_CSV} -> {backup}")
        RESULTS_CSV.rename(backup)

    ensure_files_exist()

    with RESULTS_CSV.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["k", "run", "elapsed_ms"])

    print("Initializing Mininet topology...")
    net = make_net()
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')
    print(f"Client IP (h1): {h1.IP()}, Server IP (h2): {h2.IP()}")

    # quick connectivity test
    ping = h1.cmd(f"ping -c 1 {h2.IP()}")
    if "1 received" not in ping and "1 packets received" not in ping:
        print("Error: Ping failed between h1 and h2. Aborting.")
        print(ping)
        net.stop()
        sys.exit(1)
    print("Network connectivity OK")

    try:
        total = len(K_VALUES) * RUNS_PER_K
        cnt = 0
        for k in K_VALUES:
            print(f"\n--- Testing k = {k} ---")
            for run in range(1, RUNS_PER_K + 1):
                cnt += 1
                print(f"Experiment {cnt}/{total} (k={k}, run={run})")
                elapsed = run_single_experiment(net, k, run)
                if elapsed is not None:
                    with RESULTS_CSV.open("a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([k, run, elapsed])
                    print("Result saved")
                else:
                    print("Experiment failed - result not saved")
                time.sleep(0.4)
        print(f"\nAll experiments finished. Results in {RESULTS_CSV}")
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        print("Stopping Mininet...")
        net.stop()

if __name__ == "__main__":
    import os
    if os.geteuid() != 0:
        print("This script requires root (Mininet). Run with: sudo python3 run_experiments.py")
        sys.exit(1)
    main()
