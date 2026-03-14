#!/usr/bin/env python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

# Default network parameters
DEFAULT_CLIENTS = 10
BANDWIDTH = 1  # Mbps (hardcoded as per assignment)
DELAY = '10ms'
BUFFER_SIZE = 100  # packets

class SimpleTopo(Topo):
    def __init__(self, num_clients=DEFAULT_CLIENTS):
        Topo.__init__(self)
        
        # Create switch
        switch = self.addSwitch('s1', cls=OVSSwitch)
        
        # Create server
        server = self.addHost('server', ip='10.0.0.100')
        
        # Create clients
        clients = []
        for i in range(num_clients):
            client = self.addHost(f'client{i+1}', ip=f'10.0.0.{i+1}')
            clients.append(client)
        
        # Connect server to switch with specified bandwidth
        self.addLink(server, switch, bw=BANDWIDTH, delay=DELAY, max_queue_size=BUFFER_SIZE)
        
        # Connect all clients to switch with specified bandwidth
        for client in clients:
            self.addLink(client, switch, bw=BANDWIDTH, delay=DELAY, max_queue_size=BUFFER_SIZE)

def create_network(num_clients=DEFAULT_CLIENTS):
    """Create and start the network with specified parameters"""
    setLogLevel('warning')  # Reduce Mininet verbosity
    
    topo = SimpleTopo(num_clients)
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, autoSetMacs=True)
    
    net.start()
    
    # Wait a moment for the network to stabilize
    import time
    time.sleep(1)
    
    return net

def test_connectivity(net):
    """Test basic connectivity in the network"""
    print("Testing network connectivity...")
    
    server = net.get('server')
    client1 = net.get('client1')
    
    # Test ping from client1 to server
    result = client1.cmd('ping -c 1 10.0.0.100')
    if '1 received' in result:
        print("✓ Network connectivity test passed")
        return True
    else:
        print("✗ Network connectivity test failed")
        print(f"Ping result: {result}")
        return False

if __name__ == '__main__':
    setLogLevel('info')
    
    print(f"Creating network with {DEFAULT_CLIENTS} clients")
    print(f"All links bandwidth: {BANDWIDTH} Mbps")
    print(f"All links delay: {DELAY}")
    print(f"All links buffer: {BUFFER_SIZE} packets")
    
    net = create_network()
    
    print("Network created successfully!")
    print("Hosts:", [h.name for h in net.hosts])
    
    # Test connectivity
    if test_connectivity(net):
        print("\nNetwork is ready for experiments!")
        print("Server IP: 10.0.0.100")
        print("Client IPs: 10.0.0.1 - 10.0.0.10")
        
        print("\nStarting Mininet CLI...")
        print("Type 'exit' to quit")
        CLI(net)
    else:
        print("Network connectivity issues detected!")
    
    net.stop()