import socket
import threading
import json

# Load config
with open("config.json") as f:
    config = json.load(f)

SERVER_IP = config["server_ip"]
SERVER_PORT = config["server_port"]
FILENAME = config["filename"]

# Load words into memory
with open(FILENAME, "r") as f:
    WORDS = f.read().strip().split(",")

def handle_client(conn, addr):
    """Handle one client connection sequentially"""
    try:
        request = conn.recv(1024).decode().strip()  # Expecting "p,k"
        if not request:
            return
        try:
            p, k = map(int, request.split(","))
        except ValueError:
            conn.sendall(b"EOF\n")
            return

        # Fetch words
        if p >= len(WORDS):
            conn.sendall(b"EOF\n")
            return

        response_words = WORDS[p:p+k]
        if len(response_words) < k:
            response_words.append("EOF")

        response = ",".join(response_words) + "\n"
        conn.sendall(response.encode())

    finally:
        conn.close()


def start_server():
    """Start the word count server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)
    print(f"[SERVER] Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        # Sequential handling (no extra thread here, so FCFS order preserved)
        handle_client(conn, addr)


if __name__ == "__main__":
    start_server()
