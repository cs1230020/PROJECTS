#!/usr/bin/env python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
import time
import sys
import re

class WordCountTopo(Topo):
    def build(self, n_clients=2):
        s1 = self.addSwitch('s1')
        server = self.addHost('server', ip='10.0.0.1/24')

        self.addLink(server, s1, cls=TCLink, bw=100)

        for i in range(1, n_clients + 1):
            client = self.addHost(f'client{i}', ip=f'10.0.0.{i+1}/24')
            self.addLink(client, s1, cls=TCLink, bw=100)

def run_experiment(n_clients):
    topo = WordCountTopo(n_clients=n_clients)
    net = Mininet(topo=topo, controller=OVSController,
                  autoSetMacs=True, autoStaticArp=True)
    net.start()

    server = net.get('server')
    clients = [net.get(f'client{i}') for i in range(1, n_clients + 1)]

    # Start server
    server.popen("python3 server.py --config config.json",
                 shell=True, stdout=open('/dev/null', 'w'),
                 stderr=open('/dev/null', 'w'))
    time.sleep(1)  # give server time to start

    completion_times = []

    for i, client in enumerate(clients, start=1):
        output = client.cmd("python3 client.py --time-only --config config.json")
        # Expect either "ELAPSED_MS:123" or "<seconds>"
        match_ms = re.search(r"ELAPSED_MS:(\d+)", output)
        match_sec = re.search(r"([0-9]+\.[0-9]+)", output)

        if match_ms:
            elapsed = int(match_ms.group(1)) / 1000.0
        elif match_sec:
            elapsed = float(match_sec.group(1))
        else:
            elapsed = None

        if elapsed is not None:
            completion_times.append(elapsed)
            print(f"client{i}: {elapsed:.6f} seconds")
        else:
            print(f"client{i}: failed (output: {output.strip()})")

    net.stop()
    return completion_times

def main():
    if len(sys.argv) < 2:
        print("Usage: sudo python3 topology.py <num_clients>")
        sys.exit(1)

    n_clients = int(sys.argv[1])
    times = run_experiment(n_clients)
    print("Completion times:", times)

if __name__ == "__main__":
    main()
