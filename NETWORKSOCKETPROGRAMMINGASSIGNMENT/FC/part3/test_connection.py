#!/usr/bin/env python3
import socket
import json
import time
import subprocess
import sys

def test_server():
    print("Testing server connection...")
    
    # Start server
    server = subprocess.Popen([sys.executable, 'server.py'], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    time.sleep(2)
    
    try:
        # Try to connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 8888))
        print("✓ Connected to server")
        
        # Send test request
        sock.send(b"0,5\n")
        response = sock.recv(1024)
        print(f"✓ Got response: {response.decode().strip()[:50]}...")
        
        sock.close()
        print("✓ Connection test successful!")
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    test_server()