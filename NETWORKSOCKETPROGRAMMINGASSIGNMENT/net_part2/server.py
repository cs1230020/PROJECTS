#!/usr/bin/env python3
import socket
import threading
import json
import time
import sys

class WordCountServer:
    def __init__(self, config_path="config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.server_ip = self.config["server_ip"]
        self.server_port = self.config["server_port"]
        self.filename = self.config["filename"]

        # Load words
        try:
            with open(self.filename, "r") as f:
                content = f.read().strip()
            self.words = [w.strip() for w in content.split(",") if w.strip()]
        except FileNotFoundError:
            print(f"Error: {self.filename} not found")
            sys.exit(1)

        self.socket = None
        self.running = False
        self.request_queue = []
        self.queue_lock = threading.Lock()

    def start_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.server_ip, self.server_port))
            self.socket.listen(64)

            print(f"Server listening on {self.server_ip}:{self.server_port}")
            print(f"Loaded {len(self.words)} words")

            self.running = True

            threading.Thread(target=self.process_requests, daemon=True).start()

            while self.running:
                client_socket, client_address = self.socket.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                ).start()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.cleanup()

    def handle_client(self, client_socket, client_address):
        try:
            data = client_socket.recv(1024).decode("utf-8").strip()
            if not data:
                client_socket.close()
                return

            with self.queue_lock:
                self.request_queue.append((client_socket, client_address, data))
        except Exception as e:
            print(f"Error with {client_address}: {e}")
            client_socket.close()

    def process_requests(self):
        while self.running:
            item = None
            with self.queue_lock:
                if self.request_queue:
                    item = self.request_queue.pop(0)

            if item:
                sock, addr, req = item
                self.handle_request(sock, addr, req)
                try:
                    sock.close()
                except:
                    pass
            else:
                time.sleep(0.001)

    def handle_request(self, client_socket, client_address, request):
        try:
            parts = request.split(",")
            if len(parts) != 2:
                response = "Invalid request\n"
            else:
                try:
                    p = int(parts[0])
                    k = int(parts[1])
                    response = self.get_words(p, k) + "\n"
                except ValueError:
                    response = "Invalid parameters\n"

            client_socket.sendall(response.encode("utf-8"))
        except Exception as e:
            print(f"Error processing {client_address}: {e}")

    def get_words(self, offset, count):
        if offset >= len(self.words):
            return "EOF"
        end = min(offset + count, len(self.words))
        chunk = self.words[offset:end]
        if end == len(self.words) and len(chunk) < count:
            chunk.append("EOF")
        return ",".join(chunk)

    def cleanup(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("Server stopped")

def main():
    server = WordCountServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        server.cleanup()

if __name__ == "__main__":
    main()
