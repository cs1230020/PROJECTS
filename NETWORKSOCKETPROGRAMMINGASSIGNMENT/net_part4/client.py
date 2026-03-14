#!/usr/bin/env python3

import socket
import time
import json
import argparse
import logging
from collections import defaultdict

class WordCountClient:
    def __init__(self, server_ip, port, batch_size=1, client_id="client"):
        self.server_ip = server_ip
        self.port = port
        self.batch_size = batch_size  # Number of full downloads (c parameter)
        self.client_id = client_id
        
        # Configure logging
        log_filename = f'logs/{client_id}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(f'client_{client_id}')
    
    def download_words(self):
        """Download words from server and count frequencies"""
        word_counts = defaultdict(int)
        
        try:
            # Connect to server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30.0)
            sock.connect((self.server_ip, self.port))
            self.logger.info(f"Connected to server {self.server_ip}:{self.port}")
            
            start_time = time.time()
            
            # For rogue client, download the file multiple times (batch_size times)
            for batch in range(self.batch_size):
                self.logger.info(f"Starting download batch {batch + 1}/{self.batch_size}")
                
                p = 0  # Start offset
                k = 5  # Words per request (fixed as per assignment)
                
                while True:
                    # Send request
                    request = f"{p},{k}\n"
                    sock.send(request.encode())
                    self.logger.debug(f"Sent request: {p},{k}")
                    
                    # Receive response
                    response = sock.recv(4096).decode().strip()
                    self.logger.debug(f"Received: {response}")
                    
                    if not response:
                        break
                    
                    # Check for EOF
                    if response == "EOF":
                        break
                    
                    # Parse words
                    words = [word.strip() for word in response.split(',') if word.strip()]
                    
                    # Check if EOF is in the response
                    if "EOF" in words:
                        words.remove("EOF")
                        # Count remaining words
                        for word in words:
                            if word:
                                word_counts[word] += 1
                        break
                    
                    # Count words
                    for word in words:
                        if word:
                            word_counts[word] += 1
                    
                    # Move to next batch of words
                    p += k
                
                self.logger.info(f"Completed download batch {batch + 1}/{self.batch_size}")
            
            end_time = time.time()
            completion_time = end_time - start_time
            
            sock.close()
            
            # Log completion time (this will be parsed by the runner)
            self.logger.info(f"COMPLETION_TIME: {completion_time:.6f}")
            
            # Print word frequencies
            print(f"\nWord frequencies for {self.client_id}:")
            for word, count in sorted(word_counts.items()):
                print(f"{word}: {count}")
            
            return completion_time, word_counts
            
        except Exception as e:
            self.logger.error(f"Error in download: {e}")
            return None, {}
    
    def run(self):
        """Run the client"""
        self.logger.info(f"Starting client {self.client_id} with batch_size={self.batch_size}")
        
        completion_time, word_counts = self.download_words()
        
        if completion_time:
            self.logger.info(f"Client {self.client_id} completed in {completion_time:.6f} seconds")
            return completion_time
        else:
            self.logger.error(f"Client {self.client_id} failed")
            return None

def main():
    parser = argparse.ArgumentParser(description='Word Count Client for Part 4')
    parser.add_argument('--batch-size', type=int, default=1, 
                       help='Number of times to download the full file (c parameter)')
    parser.add_argument('--client-id', type=str, default='client',
                       help='Client identifier for logging')
    parser.add_argument('--config', type=str, default='config.json',
                       help='Configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    # Create logs directory
    import os
    os.makedirs('logs', exist_ok=True)
    
    # Create and run client
    client = WordCountClient(
        server_ip=config['server_ip'],
        port=config['port'],
        batch_size=args.batch_size,
        client_id=args.client_id
    )
    
    completion_time = client.run()
    
    if completion_time:
        print(f"Client {args.client_id} completed successfully in {completion_time:.6f} seconds")
    else:
        print(f"Client {args.client_id} failed")

if __name__ == '__main__':
    main()