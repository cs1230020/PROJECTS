
import socket
import threading
import queue
import json
import time
import sys
from collections import defaultdict, deque, OrderedDict

class RoundRobinServer:
    def __init__(self, config):
        self.config = config
        self.client_queues = {}  
        self.client_sockets = {}  
        self.client_order = []  
        self.current_client_index = 0
        self.lock = threading.Lock()
        
        
        try:
            with open(config['filename'], 'r') as f:
                content = f.read().strip()
                self.words = [word.strip() for word in content.split(',')]
            print(f"Loaded {len(self.words)} words from {config['filename']}")
        except FileNotFoundError:
            print(f"Error: File {config['filename']} not found!")
            sys.exit(1)
    
    def register_client(self, client_id, client_socket):
        
        with self.lock:
            if client_id not in self.client_queues:
                self.client_queues[client_id] = deque()
                self.client_sockets[client_id] = client_socket
                self.client_order.append(client_id)
                print(f"Registered client {client_id} (Total clients: {len(self.client_order)})")
    
    def unregister_client(self, client_id):
        
        with self.lock:
            if client_id in self.client_queues:
                del self.client_queues[client_id]
            if client_id in self.client_sockets:
                del self.client_sockets[client_id]
            if client_id in self.client_order:
                self.client_order.remove(client_id)
                
                if self.current_client_index >= len(self.client_order) and len(self.client_order) > 0:
                    self.current_client_index = 0
            print(f"Unregistered client {client_id} (Remaining clients: {len(self.client_order)})")
    
    def add_request(self, client_id, request):
        
        with self.lock:
            if client_id in self.client_queues:
                self.client_queues[client_id].append(request)
                print(f"Added request from {client_id}: {request.strip()} (Queue size: {len(self.client_queues[client_id])})")
    
    def handle_client(self, client_socket, addr):
        
        client_id = f"{addr[0]}:{addr[1]}"
        print(f"New client connected: {client_id}")
        
        
        self.register_client(client_id, client_socket)
        
        try:
            buffer = ""
            while True:
                
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                buffer += data
                
                
                while '\n' in buffer:
                    request, buffer = buffer.split('\n', 1)
                    if request:
                        
                        self.add_request(client_id, request)
                        
        except ConnectionResetError:
            print(f"Client {client_id} disconnected unexpectedly")
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            
            self.unregister_client(client_id)
            client_socket.close()
            print(f"Client {client_id} disconnected")
    
    def get_next_request(self):
        
        with self.lock:
            if not self.client_order:
                return None, None, None
            
            
            for _ in range(len(self.client_order)):
                if not self.client_order:  
                    return None, None, None
                    
                
                client_id = self.client_order[self.current_client_index]
                
                
                self.current_client_index = (self.current_client_index + 1) % len(self.client_order)
                
                
                if client_id in self.client_queues and self.client_queues[client_id]:
                    request = self.client_queues[client_id].popleft()
                    client_socket = self.client_sockets.get(client_id)
                    if client_socket:
                        return client_socket, request, client_id
            
            
            return None, None, None
        
    def process_requests(self):
        
        print("Round-robin processor started")
        
        while True:
            
            client_socket, request, client_id = self.get_next_request()
            
            if client_socket is None:
                
                time.sleep(0.001)
                continue
            
            try:
                
                parts = request.strip().split(',')
                if len(parts) != 2:
                    print(f"Invalid request format: {request}")
                    continue
                
                offset = int(parts[0])
                k = int(parts[1])
                
                print(f"Processing request from {client_id}: offset={offset}, k={k}")
                
                
                response = self.get_words(offset, k)
                
                
                try:
                    client_socket.send(response.encode())
                    print(f"Sent response to {client_id}: {len(response)} bytes")
                except Exception as e:
                    print(f"Error sending response to {client_id}: {e}")
                        
            except Exception as e:
                print(f"Error processing request: {e}")
        
    def get_words(self, offset, k):
        
        if offset >= len(self.words):
            return "EOF\n"
        
        end = min(offset + k, len(self.words))
        selected_words = self.words[offset:end]
        
        
        if end >= len(self.words):
            selected_words.append("EOF")
        
        return ','.join(selected_words) + '\n'
    
    def start(self):
        
        
        processor = threading.Thread(target=self.process_requests, daemon=True)
        processor.start()
        
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.config['server_ip'], self.config['server_port']))
        except OSError as e:
            print(f"Error binding to {self.config['server_ip']}:{self.config['server_port']}: {e}")
            print("Make sure the IP address is correct for your system")
            sys.exit(1)
            
        server_socket.listen(50)
        
        print(f"Round-Robin Server listening on {self.config['server_ip']}:{self.config['server_port']}")
        print("="*60)
        print("Round-Robin Scheduling Active:")
        print("- Each client gets one request processed per turn")
        print("- Prevents any client from monopolizing the server")
        print("="*60)
        print("Press Ctrl+C to stop the server\n")
        
        try:
            while True:
                client_socket, addr = server_socket.accept()
                
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, addr),
                    daemon=True
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n\nServer shutting down...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server_socket.close()
            print("Server stopped")

def main():
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json file not found!")
        print("Creating default config.json...")
        config = {
            "server_ip": "0.0.0.0",
            "server_port": 8888,
            "k": 5,
            "p": 0,
            "filename": "words.txt",
            "num_repetitions": 5,
            "num_clients": 10,
            "c": 1
        }
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    
    if config['server_ip'] == '10.0.0.1':
        print("Note: Changing server IP from 10.0.0.1 to 0.0.0.0 for local testing")
        config['server_ip'] = '0.0.0.0'
    
    
    server = RoundRobinServer(config)
    server.start()

if __name__ == "__main__":
    main()