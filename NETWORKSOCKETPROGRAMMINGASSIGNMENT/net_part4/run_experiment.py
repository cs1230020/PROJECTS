#!/usr/bin/env python3
import json
import os
import time
import glob
import re
import csv
from collections import defaultdict

class ExperimentRunner:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.server_ip = self.config['server_ip']
        self.port = self.config['port']
        self.num_clients = self.config['num_clients']
        self.c = self.config['c']  # starting batch size
        self.p = self.config['p']
        self.k = self.config['k']

    def cleanup_logs(self):
        if os.path.exists("logs"):
            for log in glob.glob("logs/*.log"):
                os.remove(log)
        else:
            os.makedirs("logs", exist_ok=True)

    def parse_logs(self):
        completion_times = {'rogue': [], 'normal': []}
        for log_file in glob.glob("logs/*.log"):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    matches = re.findall(r'COMPLETION_TIME: ([\d.]+)', content)
                    if matches:
                        t = float(matches[-1])
                        if 'rogue' in os.path.basename(log_file):
                            completion_times['rogue'].append(t)
                        else:
                            completion_times['normal'].append(t)
            except Exception as e:
                print(f"Error parsing {log_file}: {e}")
        return completion_times

    def calculate_jfi(self, completion_times):
        utilities = [1.0/t for t in completion_times if t>0]
        n = len(utilities)
        if n == 0: return 0.0
        s1 = sum(utilities)
        s2 = sum(u*u for u in utilities)
        if s2 == 0: return 0.0
        return (s1*s1)/(n*s2)

    def run_experiment(self, c_value):
        print(f"Running experiment with c={c_value}")
        self.cleanup_logs()

        try:
            from topology import create_network
        except ImportError:
            print("Error: topology.py not found, skipping Mininet network")
            return {'rogue': [], 'normal': []}

        net = create_network(num_clients=self.num_clients)
        try:
            server = net.get('server')
            clients = [net.get(f'client{i+1}') for i in range(self.num_clients)]
            server_proc = server.popen("python3 server.py", stdout=None, stderr=None)
            time.sleep(3)

            rogue_proc = clients[0].popen(f"python3 client.py --batch-size {c_value} --client-id rogue", stdout=None, stderr=None)
            normal_procs = []
            for i in range(1, self.num_clients):
                proc = clients[i].popen(f"python3 client.py --batch-size 1 --client-id normal_{i+1}", stdout=None, stderr=None)
                normal_procs.append(proc)

            rogue_proc.wait()
            for proc in normal_procs: proc.wait()
            server_proc.terminate()
            server_proc.wait()
            time.sleep(2)

            return self.parse_logs()

        except Exception as e:
            print(f"Error in experiment: {e}")
            return {'rogue': [], 'normal': []}
        finally:
            try: net.stop()
            except: pass

    def run_varying_c(self, min_c=1, max_c=10):
        os.makedirs('results', exist_ok=True)
        c_values = list(range(min_c, max_c+1))
        all_results = {}
        jfi_values = []

        for c in c_values:
            results = self.run_experiment(c)
            all_results[c] = results
            all_times = results['rogue'] + results['normal']
            jfi = self.calculate_jfi(all_times) if all_times else 0.0
            jfi_values.append(jfi)
            print(f"c={c} JFI={jfi:.4f}")

        # Save CSV
        with open('results/part4_results.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['c_value', 'jfi', 'rogue_times', 'normal_times'])
            for i, c in enumerate(c_values):
                rogue_times = ';'.join(map(str, all_results[c]['rogue']))
                normal_times = ';'.join(map(str, all_results[c]['normal']))
                writer.writerow([c, jfi_values[i], rogue_times, normal_times])
        print("Results saved to results/part4_results.csv")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--single-run', action='store_true')
    parser.add_argument('--config', type=str, default='config.json')
    args = parser.parse_args()

    runner = ExperimentRunner(args.config)
    if args.single_run:
        runner.run_experiment(runner.c)
    else:
        runner.run_varying_c()
