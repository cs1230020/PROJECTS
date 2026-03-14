#!/usr/bin/env python3

import socket
import threading
import json
import time
import sys
import os
import queue
from datetime import datetime

class FCFSServer:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.server_ip = self.config['server_ip']
        self.port = self.config['port']
        self.filename = "words.txt"
        
        # Load words from file
        self.words = []
        try:
            with open(self.filename, 'r') as f:
                content = f.read().strip()
                if content:
                    self.words = [word.strip() for word in content.split(',')]
        except FileNotFoundError:
            print(f"Error: {self.filename} not found")
            sys.exit(1)
        
        self.socket = None
        self.running = False
        
        # FCFS request queue - processes requests in order of arrival
        self.request_queue = queue.Queue()
        self.processing_thread = None
        
        # Client tracking for logging
        self.client_connections = {}
        self.request_counter = 0
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        print(f"FCFS Server initialized with {len(self.words)} words")
        
    def start_server(self):
        """Start the FCFS server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.server_ip, self.port))
            self.socket.listen(20)  # Allow many pending connections
            
            print(f"FCFS Server listening on {self.server_ip}:{self.port}")
            
            self.running = True
            
            # Start the FCFS request processing thread
            self.processing_thread = threading.Thread(target=self.process_requests_fcfs)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            # Accept connections
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    print(f"New connection from {client_address}")
                    
                    # Start a thread to handle this client's requests
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("Error accepting connection")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket, client_address):
        """Handle a single client connection - receives requests and queues them"""
        client_id = f"{client_address[0]}:{client_address[1]}"
        self.client_connections[client_id] = {
            'socket': client_socket,
            'address': client_address,
            'requests_sent': 0
        }
        
        try:
            while True:
                # Receive request from client
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    break
                
                # Parse request to get client metadata if included
                request_parts = data.split('|')
                actual_request = request_parts[0]  # p,k format
                client_type = request_parts[1] if len(request_parts) > 1 else "unknown"
                client_name = request_parts[2] if len(request_parts) > 2 else client_id
                
                arrival_time = time.time()
                self.request_counter += 1
                
                print(f"Received request {self.request_counter} from {client_name} ({client_type}): {actual_request}")
                
                # Create request item for FCFS queue
                request_item = {
                    'request_id': self.request_counter,
                    'client_socket': client_socket,
                    'client_address': client_address,
                    'client_id': client_id,
                    'client_name': client_name,
                    'client_type': client_type,
                    'request': actual_request,
                    'arrival_time': arrival_time
                }
                
                # Add to FCFS queue (blocking if queue is full)
                self.request_queue.put(request_item)
                self.client_connections[client_id]['requests_sent'] += 1
                
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            if client_id in self.client_connections:
                del self.client_connections[client_id]
            print(f"Connection closed: {client_address}")
    
    def process_requests_fcfs(self):
        """Process requests in FCFS order (First Come First Serve)"""
        print("FCFS processing thread started")
        
        while self.running:
            try:
                # Get next request from queue (blocks if empty)
                request_item = self.request_queue.get(timeout=1.0)
                
                start_processing_time = time.time()
                
                # Process the request
                response = self.handle_request(request_item['request'])
                
                end_processing_time = time.time()
                processing_duration = end_processing_time - start_processing_time
                total_wait_time = start_processing_time - request_item['arrival_time']
                
                # Send response back to client
                try:
                    request_item['client_socket'].send((response + '\n').encode('utf-8'))
                    
                    # Log the request completion
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'request_id': request_item['request_id'],
                        'client_name': request_item['client_name'],
                        'client_type': request_item['client_type'],
                        'arrival_time': request_item['arrival_time'],
                        'start_processing_time': start_processing_time,
                        'end_processing_time': end_processing_time,
                        'processing_duration': processing_duration,
                        'wait_time': total_wait_time,
                        'request': request_item['request'],
                        'response_length': len(response)
                    }
                    
                    self.log_request(log_entry)
                    
                    print(f"Processed request {request_item['request_id']} from {request_item['client_name']} "
                          f"(wait: {total_wait_time:.4f}s, process: {processing_duration:.4f}s)")
                
                except Exception as e:
                    print(f"Error sending response to {request_item['client_name']}: {e}")
                
                # Mark task as done
                self.request_queue.task_done()
                
            except queue.Empty:
                # No requests in queue, continue
                continue
            except Exception as e:
                print(f"Error in FCFS processing: {e}")
    
    def handle_request(self, request):
        """Process a single p,k request and return response"""
        try:
            parts = request.split(',')
            if len(parts) != 2:
                return "Invalid request format"
            
            p = int(parts[0])  # offset
            k = int(parts[1])  # number of words
            
            return self.get_words(p, k)
            
        except ValueError:
            return "Invalid parameters"
    
    def get_words(self, offset, count):
        """Get words starting from offset"""
        if offset >= len(self.words):
            return "EOF"
        
        end_idx = min(offset + count, len(self.words))
        selected_words = self.words[offset:end_idx]
        
        # If we've reached the end of file
        if end_idx == len(self.words) and len(selected_words) < count:
            selected_words.append("EOF")
        
        return ','.join(selected_words)
    
    def log_request(self, log_entry):
        """Log request details to file"""
        log_filename = f"logs/{log_entry['client_name']}.log"
        
        with open(log_filename, 'a') as f:
            f.write(f"{log_entry['timestamp']}|"
                   f"{log_entry['request_id']}|"
                   f"{log_entry['client_type']}|"
                   f"{log_entry['arrival_time']:.6f}|"
                   f"{log_entry['start_processing_time']:.6f}|"
                   f"{log_entry['end_processing_time']:.6f}|"
                   f"{log_entry['processing_duration']:.6f}|"
                   f"{log_entry['wait_time']:.6f}|"
                   f"{log_entry['request']}|"
                   f"{log_entry['response_length']}\n")
    
    def cleanup(self):
        """Clean up server resources"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("FCFS Server stopped")

def main():
    server = FCFSServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nServer interrupted")
        server.cleanup()

if __name__ == "__main__":
    main()
