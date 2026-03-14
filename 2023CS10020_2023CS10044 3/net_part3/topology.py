#!/usr/bin/env python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink

class Topo1(Topo):
    def __init__(self,n=10):
        Topo.__init__(self)
        s=self.addSwitch("s1")
        self.addHost("server",ip="10.0.0.100")
        for i in range(n): self.addHost(f"client{i+1}",ip=f"10.0.0.{i+1}")
        self.addLink("server",s,bw=1,delay="10ms",max_queue_size=100)
        for i in range(n): self.addLink(f"client{i+1}",s,bw=1,delay="10ms",max_queue_size=100)

def create_network(n=10):
    return Mininet(topo=Topo1(n),switch=OVSSwitch,link=TCLink)

