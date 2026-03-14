# client.py
import socket
import threading
import time
import json
import sys
import os
import random

class ResultCollector:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
    
    def add(self, result):
        with self.lock:
            self.results.append(result)
    
    def get_all(self):
        with self.lock:
            return sorted(self.results, key=lambda x: x['client_id'])

def normal_client(client_id, config, collector, barrier=None):
    """Normal client - sends one request at a time, waits for response"""
    try:
        if barrier:
            barrier.wait()  # Synchronized start
        
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(120)
        sock.connect(('127.0.0.1', config['server_port']))
        
        offset = 0
        all_words = []
        request_count = 0
        
        while True:
            # Send request
            request = f"{offset},{config['k']}\n"
            sock.send(request.encode())
            request_count += 1
            
            # Wait for complete response before sending next
            response = ""
            while '\n' not in response:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk.decode()
            
            response = response.strip()
            if not response:
                break
                
            words = response.split(',')
            
            if 'EOF' in words:
                words = [w for w in words if w != 'EOF']
                if words:
                    all_words.extend(words)
                break
            
            all_words.extend(words)
            offset += config['k']
            
            # Small random delay to simulate real client behavior
            time.sleep(random.uniform(0.001, 0.005))
        
        sock.close()
        completion_time = time.time() - start_time
        
        collector.add({
            'client_id': client_id,
            'type': 'normal',
            'completion_time': completion_time,
            'words_count': len(all_words),
            'request_count': request_count
        })
        
        print(f"Normal Client {client_id}: Completed in {completion_time:.3f}s ({request_count} requests)")
        
    except Exception as e:
        print(f"Normal Client {client_id}: Error - {e}")
        collector.add({
            'client_id': client_id,
            'type': 'normal',
            'completion_time': -1,
            'words_count': 0,
            'request_count': 0
        })

def greedy_client(client_id, config, c, collector, barrier=None):
    """
    Greedy client - sends exactly c requests initially without waiting
    When c=1, behaves like normal client. When c>1, floods the queue.
    """
    try:
        if barrier:
            barrier.wait()  # Synchronized start
        
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(120)
        sock.connect(('127.0.0.1', config['server_port']))
        
        # Calculate total requests needed
        with open(config['filename'], 'r') as f:
            total_words = len(f.read().strip().split(','))
        total_requests_needed = (total_words + config['k'] - 1) // config['k']
        
        all_words = []
        offset = 0
        requests_sent = 0
        responses_needed = 0
        
        # GREEDY: Send exactly c requests initially (not c*2!)
        burst_size = min(c, total_requests_needed)
        
        if c > 1:
            print(f"Greedy Client {client_id}: Sending burst of {burst_size} requests...")
        
        # Send initial burst of requests
        for i in range(burst_size):
            request = f"{offset},{config['k']}\n"
            sock.send(request.encode())
            requests_sent += 1
            responses_needed += 1
            offset += config['k']
        
        if c > 1:
            print(f"Greedy Client {client_id}: Sent {burst_size} requests in burst!")
        
        # Now process responses and send more requests as needed
        eof_received = False
        buffer = ""
        
        while responses_needed > 0 and not eof_received:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()
                
                # Process all complete responses
                while '\n' in buffer:
                    response, buffer = buffer.split('\n', 1)
                    if response:
                        responses_needed -= 1
                        words = response.split(',')
                        
                        if 'EOF' in words:
                            words = [w for w in words if w != 'EOF']
                            if words:
                                all_words.extend(words)
                            eof_received = True
                            break
                        else:
                            all_words.extend(words)
                            
                            # Send another request if needed
                            if not eof_received and requests_sent < total_requests_needed:
                                request = f"{offset},{config['k']}\n"
                                sock.send(request.encode())
                                requests_sent += 1
                                responses_needed += 1
                                offset += config['k']
                                
            except socket.timeout:
                print(f"Greedy Client {client_id}: Timeout")
                break
        
        sock.close()
        completion_time = time.time() - start_time
        
        collector.add({
            'client_id': client_id,
            'type': 'greedy',
            'completion_time': completion_time,
            'words_count': len(all_words),
            'request_count': requests_sent,
            'burst_size': burst_size,
            'c': c
        })
        
        print(f"Greedy Client {client_id}: Completed in {completion_time:.3f}s")
        if c > 1:
            print(f"  -> Sent {requests_sent} requests (initial burst: {burst_size})")
        
    except Exception as e:
        print(f"Greedy Client {client_id}: Error - {e}")
        collector.add({
            'client_id': client_id,
            'type': 'greedy',
            'completion_time': -1,
            'words_count': 0,
            'request_count': 0,
            'burst_size': 0,
            'c': c
        })

def calculate_jfi(times):
    """Calculate Jain's Fairness Index"""
    valid = [t for t in times if t > 0]
    if not valid:
        return 0
    
    n = len(valid)
    sum_sq = sum(valid) ** 2
    sum_of_sq = sum(t**2 for t in valid)
    
    if sum_of_sq == 0:
        return 0
    
    return sum_sq / (n * sum_of_sq)

def run_experiment(config):
    """Run experiment with 9 normal and 1 greedy client"""
    print(f"\n{'='*60}")
    print(f"Running FCFS experiment with c={config['c']}")
    print(f"{'='*60}\n")
    
    collector = ResultCollector()
    threads = []
    
    # Use barrier for synchronized start
    num_clients = config.get('num_clients', 10)
    barrier = threading.Barrier(num_clients)
    
    # Always make the last client greedy for consistency
    print(f"Starting {num_clients} clients (Client {num_clients-1} will be greedy)...")
    
    # Start normal clients
    for i in range(num_clients - 1):
        t = threading.Thread(
            target=normal_client,
            args=(i, config, collector, barrier)
        )
        t.daemon = True
        threads.append(t)
        t.start()
    
    # Start greedy client
    t = threading.Thread(
        target=greedy_client,
        args=(num_clients - 1, config, config['c'], collector, barrier)
    )
    t.daemon = True
    threads.append(t)
    t.start()
    
    print("All clients started, waiting for completion...")
    
    # Wait for all threads
    for t in threads:
        t.join(timeout=180)
        if t.is_alive():
            print(f"Warning: Thread still alive after timeout")
    
    return collector.get_all()

def print_results(results):
    """Print detailed results"""
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"{'ID':<4} {'Type':<8} {'Time (s)':<12} {'Words':<8} {'Requests':<10}")
    print(f"{'-'*70}")
    
    completion_times = []
    normal_times = []
    greedy_time = 0
    
    for r in results:
        if r['completion_time'] > 0:
            completion_times.append(r['completion_time'])
            
            if r['type'] == 'normal':
                normal_times.append(r['completion_time'])
                print(f"{r['client_id']:<4} {r['type']:<8} {r['completion_time']:<12.3f} "
                      f"{r['words_count']:<8} {r['request_count']:<10}")
            else:  # greedy
                greedy_time = r['completion_time']
                print(f"{r['client_id']:<4} {r['type']:<8} {r['completion_time']:<12.3f} "
                      f"{r['words_count']:<8} {r['request_count']:<10} (burst={r.get('burst_size', 0)})")
        else:
            print(f"{r['client_id']:<4} {r['type']:<8} {'FAILED':<12} "
                  f"{r['words_count']:<8} {r['request_count']:<10}")
    
    if completion_times:
        jfi = calculate_jfi(completion_times)
        print(f"\n{'='*70}")
        print(f"Jain's Fairness Index: {jfi:.4f}")
        
        if normal_times:
            avg_normal = sum(normal_times) / len(normal_times)
            min_normal = min(normal_times)
            max_normal = max(normal_times)
            
            print(f"Normal client times: avg={avg_normal:.3f}s, min={min_normal:.3f}s, max={max_normal:.3f}s")
            
            if greedy_time > 0:
                print(f"Greedy client time: {greedy_time:.3f}s")
                if avg_normal > 0:
                    ratio = greedy_time / avg_normal
                    print(f"Greedy/Normal ratio: {ratio:.3f}")
                    if ratio < 1:
                        print(f"Greedy advantage: {(1-ratio)*100:.1f}% faster than average normal")
                    else:
                        print(f"No advantage - greedy is {(ratio-1)*100:.1f}% slower")
        
        print(f"{'='*70}")

def main():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Run experiment
    results = run_experiment(config)
    
    # Print results
    print_results(results)
    
    # Save results
    output_file = f"results_c{config['c']}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()