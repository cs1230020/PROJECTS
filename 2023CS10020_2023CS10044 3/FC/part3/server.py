# server.py
import socket
import threading
import queue
import json
import time
import sys
from collections import defaultdict

class FCFSServer:
    def __init__(self, config):
        self.config = config
        self.request_queue = queue.Queue()
        self.running = True
        self.client_request_counts = defaultdict(int)
        self.request_id_counter = 0
        self.request_id_lock = threading.Lock()
        self.start_time = time.time()
        
        # Load words from file
        try:
            with open(config['filename'], 'r') as f:
                content = f.read().strip()
                self.words = [word.strip() for word in content.split(',')]
            print(f"Loaded {len(self.words)} words from {config['filename']}")
        except FileNotFoundError:
            print(f"Error: File {config['filename']} not found!")
            sys.exit(1)
    
    def handle_client(self, client_socket, addr):
        """Handle incoming client connections"""
        client_id = f"{addr[0]}:{addr[1]}"
        print(f"[{time.time()-self.start_time:.2f}] New client connected: {client_id}")
        
        try:
            buffer = ""
            client_socket.settimeout(120)  # 2 minute timeout
            
            while True:
                # Receive data
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    buffer += data.decode()
                    
                    # Process complete requests (ending with \n)
                    while '\n' in buffer:
                        request, buffer = buffer.split('\n', 1)
                        if request:
                            # Assign request ID for FCFS ordering
                            with self.request_id_lock:
                                request_id = self.request_id_counter
                                self.request_id_counter += 1
                            
                            # Add to queue with timestamp for true FCFS
                            self.request_queue.put((
                                request_id,  # For FCFS ordering
                                time.time(), # Timestamp
                                client_socket, 
                                request, 
                                client_id
                            ))
                            self.client_request_counts[client_id] += 1
                            
                except socket.timeout:
                    break
                except:
                    break
                    
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            print(f"[{time.time()-self.start_time:.2f}] Client {client_id} handler done - Queued {self.client_request_counts[client_id]} requests")
    
    def process_requests(self):
        """Process requests in strict FCFS order"""
        processed_count = 0
        
        print("FCFS processor started")
        
        while self.running:
            try:
                # Get next request from queue (strict FCFS)
                request_id, timestamp, client_socket, request, client_id = self.request_queue.get(timeout=1)
                
                processed_count += 1
                queue_time = time.time() - timestamp
                
                # Parse request
                try:
                    parts = request.strip().split(',')
                    if len(parts) != 2:
                        continue
                    
                    offset = int(parts[0])
                    k = int(parts[1])
                    
                    # CRITICAL: Processing delay - this makes FCFS queue effects visible
                    # Increase this to make the unfairness more pronounced
                    time.sleep(0.02)  # 20ms processing time per request
                    
                    # Get words
                    response = self.get_words(offset, k)
                    
                    # Send response
                    try:
                        client_socket.send(response.encode())
                        if processed_count % 50 == 0 or queue_time > 1.0:
                            print(f"[{time.time()-self.start_time:.2f}] Processed request #{processed_count} from {client_id} (queued for {queue_time:.3f}s)")
                    except (BrokenPipeError, ConnectionResetError):
                        pass  # Client disconnected
                    except Exception as e:
                        pass
                        
                except ValueError:
                    pass
                    
            except queue.Empty:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error processing request: {e}")
    
    def get_words(self, offset, k):
        """Get k words starting from offset"""
        if offset >= len(self.words):
            return "EOF\n"
        
        end = min(offset + k, len(self.words))
        selected_words = self.words[offset:end]
        
        if end >= len(self.words):
            selected_words.append("EOF")
        
        return ','.join(selected_words) + '\n'
    
    def start(self):
        """Start the server"""
        # Start request processor thread
        processor = threading.Thread(target=self.process_requests, daemon=True)
        processor.start()
        
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.bind(('0.0.0.0', self.config['server_port']))
        server_socket.listen(100)  # Increase backlog
        
        print(f"FCFS Server listening on 0.0.0.0:{self.config['server_port']}")
        print("Processing delay: 20ms per request")
        print("="*60)
        
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
            print("\nServer shutting down...")
            self.running = False
        finally:
            server_socket.close()

def main():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json file not found!")
        sys.exit(1)
    
    server = FCFSServer(config)
    server.start()

if __name__ == "__main__":
    main()