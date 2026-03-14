import socket
import json
import time
import threading

# Load config
with open("config.json") as f:
    config = json.load(f)

SERVER_IP = config["server_ip"]
SERVER_PORT = config["server_port"]
K = config["k"]
NUM_CLIENTS = config["num_clients"]

results = []  # Store completion times


def run_client(client_id):
    """One client downloads the entire file"""
    start_time = time.time()
    offset = 0
    word_count = {}

    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, SERVER_PORT))
        request = f"{offset},{K}\n"
        s.sendall(request.encode())
        response = s.recv(4096).decode().strip()
        s.close()

        words = response.split(",")
        if "EOF" in words:
            words = [w for w in words if w != "EOF"]
            for w in words:
                word_count[w] = word_count.get(w, 0) + 1
            break

        for w in words:
            word_count[w] = word_count.get(w, 0) + 1
        offset += K

    end_time = time.time()
    completion_time = end_time - start_time
    results.append((client_id, completion_time))
    print(f"[Client {client_id}] Finished in {completion_time:.4f} seconds")


def main():
    threads = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=run_client, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    avg_time = sum(t for _, t in results) / NUM_CLIENTS
    print(f"\n[RESULT] Average completion time per client = {avg_time:.4f} seconds")


if __name__ == "__main__":
    main()
