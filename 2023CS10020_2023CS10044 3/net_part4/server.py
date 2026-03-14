#!/usr/bin/env python3

import socket
import threading
import time
import queue
import json
from collections import defaultdict, deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server.log'),
        logging.StreamHandler()
    ]
)

class RoundRobinServer:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        self.host = config['server_ip']
        self.port = config['port']
        self.words_file = 'words.txt'
        
        # Load words from file
        self.words = self.load_words()
        
        # Client management
        self.clients = {}  # client_id -> client_info
        self.client_queues = defaultdict(queue.Queue)  # client_id -> request queue
        self.active_clients = deque()  # Round-robin queue of active client IDs
        self.client_lock = threading.Lock()
        
        # Server socket
        self.server_socket = None
        self.running = True
        
        logging.info(f"Server initialized with {len(self.words)} words")
    
    def load_words(self):
        """Load words from the words.txt file"""
        try:
            with open(self.words_file, 'r') as f:
                content = f.read().strip()
                words = [word.strip() for word in content.split(',') if word.strip()]
                return words
        except FileNotFoundError:
            logging.error(f"Words file {self.words_file} not found")
            return []
    
    def handle_client_connection(self, client_socket, client_address):
        """Handle incoming client connections"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        
        with self.client_lock:
            self.clients[client_id] = {
                'socket': client_socket,
                'address': client_address,
                'connected': True
            }
            if client_id not in self.active_clients:
                self.active_clients.append(client_id)
        
        logging.info(f"Client {client_id} connected")
        
        try:
            while self.running:
                try:
                    # Receive request from client
                    data = client_socket.recv(1024).decode().strip()
                    if not data:
                        break
                    
                    # Add request to client's queue
                    request_time = time.time()
                    self.client_queues[client_id].put((data, request_time))
                    logging.info(f"Queued request from {client_id}: {data}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    logging.error(f"Error receiving from {client_id}: {e}")
                    break
        
        except Exception as e:
            logging.error(f"Error handling client {client_id}: {e}")
        
        finally:
            # Clean up client
            with self.client_lock:
                if client_id in self.clients:
                    self.clients[client_id]['connected'] = False
                if client_id in self.active_clients:
                    self.active_clients.remove(client_id)
            
            client_socket.close()
            logging.info(f"Client {client_id} disconnected")
    
    def process_request(self, request_data):
        """Process a single request and return response"""
        try:
            parts = request_data.split(',')
            if len(parts) != 2:
                return "ERROR: Invalid request format\n"
            
            p = int(parts[0])  # offset
            k = int(parts[1])  # number of words
            
            if p < 0 or k <= 0:
                return "ERROR: Invalid parameters\n"
            
            # Get words from offset p, k words
            if p >= len(self.words):
                return "EOF\n"
            
            end_idx = min(p + k, len(self.words))
            requested_words = self.words[p:end_idx]
            
            # If we reached end of file, add EOF
            if end_idx >= len(self.words):
                requested_words.append("EOF")
            
            response = ",".join(requested_words) + "\n"
            return response
            
        except ValueError:
            return "ERROR: Invalid request format\n"
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            return "ERROR: Server error\n"
    
    def round_robin_scheduler(self):
        """Round-robin scheduler that serves one request per client per turn"""
        logging.info("Round-robin scheduler started")
        
        while self.running:
            try:
                with self.client_lock:
                    if not self.active_clients:
                        time.sleep(0.1)
                        continue
                    
                    # Get next client in round-robin order
                    current_clients = list(self.active_clients)
                
                for client_id in current_clients:
                    if not self.running:
                        break
                    
                    # Check if client is still connected
                    if client_id not in self.clients or not self.clients[client_id]['connected']:
                        with self.client_lock:
                            if client_id in self.active_clients:
                                self.active_clients.remove(client_id)
                        continue
                    
                    # Check if client has pending requests
                    if not self.client_queues[client_id].empty():
                        try:
                            # Get one request from this client
                            request_data, request_time = self.client_queues[client_id].get_nowait()
                            
                            # Process the request
                            response = self.process_request(request_data)
                            
                            # Send response
                            client_socket = self.clients[client_id]['socket']
                            client_socket.send(response.encode())
                            
                            processing_time = time.time() - request_time
                            logging.info(f"Served {client_id}: {request_data} -> response_len={len(response)} (time: {processing_time:.3f}s)")
                            
                        except queue.Empty:
                            continue
                        except Exception as e:
                            logging.error(f"Error serving client {client_id}: {e}")
                            with self.client_lock:
                                if client_id in self.active_clients:
                                    self.active_clients.remove(client_id)
                
                # Small delay to prevent busy waiting
                time.sleep(0.001)
                
            except Exception as e:
                logging.error(f"Scheduler error: {e}")
                time.sleep(0.1)
        
        logging.info("Round-robin scheduler stopped")
    
    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(20)  # Allow up to 20 pending connections
            
            logging.info(f"Round-Robin server listening on {self.host}:{self.port}")
            
            # Start the round-robin scheduler thread
            scheduler_thread = threading.Thread(target=self.round_robin_scheduler)
            scheduler_thread.daemon = True
            scheduler_thread.start()
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_socket.settimeout(30.0)  # 30 second timeout
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client_connection,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.running:
                        logging.error(f"Error accepting connections: {e}")
                    break
        
        except Exception as e:
            logging.error(f"Server error: {e}")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logging.info("Server stopped")

def main():
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    server = RoundRobinServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        logging.info("Server interrupted by user")
    except Exception as e:
        logging.error(f"Server failed: {e}")
    finally:
        server.stop()

if __name__ == '__main__':
    main()