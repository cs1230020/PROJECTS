
import socket
import threading
import time
import json
import sys
import random
import os

class ClientResult:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
    
    def add_result(self, result):
        with self.lock:
            self.results.append(result)
    
    def get_results(self):
        with self.lock:
            return self.results.copy()

def normal_client(client_id, config, result_collector):
    
    try:
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        
        server_ip = config['server_ip']
        if server_ip == '0.0.0.0':
            server_ip = '127.0.0.1'
            
        sock.connect((server_ip, config['server_port']))
        print(f"Normal Client {client_id}: Connected to server")
        
        start_time = time.time()
        offset = 0
        all_words = []
        request_count = 0
        
        while True:
            
            request = f"{offset},{config['k']}\n"
            sock.send(request.encode())
            request_count += 1
            
            
            
            response = ""
            while '\n' not in response:
                chunk = sock.recv(4096).decode()
                if not chunk:
                    break
                response += chunk
            
            response = response.strip()
            
            
            if not response:
                break
                
            words = response.split(',')
            
            
            if 'EOF' in words:
                
                words = [w for w in words if w != 'EOF']
                all_words.extend(words)
                print(f"Normal Client {client_id}: Received EOF, total words: {len(all_words)}")
                break
            
            all_words.extend(words)
            offset += config['k']
        
        sock.close()
        completion_time = time.time() - start_time
        
        result = {
            'client_id': client_id,
            'type': 'normal',
            'completion_time': completion_time,
            'words_count': len(all_words),
            'request_count': request_count
        }
        
        result_collector.add_result(result)
        print(f"Normal Client {client_id}: Completed in {completion_time:.3f}s with {len(all_words)} words")
        
    except ConnectionRefusedError:
        print(f"Normal Client {client_id}: Could not connect to server at {server_ip}:{config['server_port']}")
    except Exception as e:
        print(f"Normal Client {client_id}: Error - {e}")
        result = {
            'client_id': client_id,
            'type': 'normal',
            'completion_time': -1,
            'words_count': 0,
            'request_count': 0
        }
        result_collector.add_result(result)

def greedy_client(client_id, config, c, result_collector):
    
    
    class SharedState:
        def __init__(self):
            self.all_words = []
            self.eof_received = False
            self.lock = threading.Lock()
            self.total_responses_received = 0

    def receiver(sock, state, semaphore):
        
        buffer = ""
        try:
            while not state.eof_received:
                chunk = sock.recv(4096).decode()
                if not chunk:
                    
                    with state.lock:
                        state.eof_received = True
                    break
                
                buffer += chunk
                
                
                while '\n' in buffer:
                    response, buffer = buffer.split('\n', 1)
                    if not response:
                        continue
                    
                    with state.lock:
                        state.total_responses_received += 1
                        words = response.split(',')
                        
                        if 'EOF' in words:
                            state.eof_received = True
                            words = [w for w in words if w != 'EOF']
                        
                        state.all_words.extend(words)
                    
                    
                    semaphore.release()

                    if state.eof_received:
                        break 
        except Exception as e:
            print(f"Greedy Client {client_id} Receiver Error: {e}")
            with state.lock:
                state.eof_received = True 
    
    try:
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_ip = config['server_ip']
        if server_ip == '0.0.0.0':
            server_ip = '127.0.0.1'
        sock.connect((server_ip, config['server_port']))
        print(f"Greedy Client {client_id}: Connected to server (c={c})")
        
        start_time = time.time()
        
        
        state = SharedState()
        
        semaphore = threading.Semaphore(c)
        
        
        recv_thread = threading.Thread(target=receiver, args=(sock, state, semaphore))
        recv_thread.start()
        
        
        offset = 0
        total_requests_sent = 0
        
        while True:
            with state.lock:
                if state.eof_received:
                    break
            
            
            semaphore.acquire()
            
            
            with state.lock:
                if state.eof_received:
                    
                    semaphore.release()
                    break

            request = f"{offset},{config['k']}\n"
            sock.send(request.encode())
            total_requests_sent += 1
            offset += config['k']

        
        recv_thread.join()
        
        sock.close()
        completion_time = time.time() - start_time
        
        result = {
            'client_id': client_id,
            'type': 'greedy',
            'completion_time': completion_time,
            'words_count': len(state.all_words),
            'request_count': total_requests_sent,
            'responses_received': state.total_responses_received,
            'c': c
        }
        
        result_collector.add_result(result)
        print(f"Greedy Client {client_id}: Completed in {completion_time:.3f}s with {len(state.all_words)} words")
        print(f"Greedy Client {client_id}: Sent {total_requests_sent} requests, received {state.total_responses_received} responses")
        
    except Exception as e:
        print(f"Greedy Client {client_id}: Main Error - {e}")
        import traceback
        traceback.print_exc()
        result = {
            'client_id': client_id,
            'type': 'greedy',
            'completion_time': -1,
            'words_count': 0,
            'request_count': 0,
            'responses_received': 0,
            'c': c,
            'error': str(e)
        }
        result_collector.add_result(result)


def run_experiment(config):
    
    print(f"\n{'='*60}")
    print(f"Running experiment with c={config['c']}")
    print(f"{'='*60}\n")
    
    threads = []
    result_collector = ClientResult()
    
    
    start_delay = 0.05
    
    
    print("Starting 9 normal clients...")
    for i in range(9):
        t = threading.Thread(
            target=normal_client,
            args=(i, config, result_collector)
        )
        threads.append(t)
        t.start()
        time.sleep(start_delay)
    
    
    print(f"\nStarting 1 greedy client with c={config['c']}...")
    t = threading.Thread(
        target=greedy_client,
        args=(9, config, config['c'], result_collector)
    )
    threads.append(t)
    t.start()
    
    
    print("\nWaiting for all clients to complete...")
    for t in threads:
        t.join()
    
    results = result_collector.get_results()
    
    
    results.sort(key=lambda x: x['client_id'])
    
    return results

def print_results(results):
    
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"{'Client ID':<10} {'Type':<10} {'Completion Time':<20} {'Words':<10}")
    print(f"{'-'*60}")
    
    for result in results:
        if result['completion_time'] > 0:
            print(f"{result['client_id']:<10} {result['type']:<10} "
                  f"{result['completion_time']:<20.3f} {result['words_count']:<10}")
        else:
            print(f"{result['client_id']:<10} {result['type']:<10} "
                  f"{'FAILED':<20} {result['words_count']:<10}")
    
    
    valid_times = [r['completion_time'] for r in results if r['completion_time'] > 0]
    if valid_times:
        avg_time = sum(valid_times) / len(valid_times)
        print(f"\nAverage completion time: {avg_time:.3f}s")
        
        
        normal_times = [r['completion_time'] for r in results 
                       if r['type'] == 'normal' and r['completion_time'] > 0]
        greedy_times = [r['completion_time'] for r in results 
                       if r['type'] == 'greedy' and r['completion_time'] > 0]
        
        if normal_times:
            print(f"Average normal client time: {sum(normal_times)/len(normal_times):.3f}s")
        if greedy_times:
            print(f"Average greedy client time: {sum(greedy_times)/len(greedy_times):.3f}s")

def main():
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json file not found!")
        sys.exit(1)
    
    
    results = run_experiment(config)
    
    
    print_results(results)
    
    
    output_file = f"results_c{config['c']}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()