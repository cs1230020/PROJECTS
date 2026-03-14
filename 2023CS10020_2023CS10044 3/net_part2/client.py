#!/usr/bin/env python3
import socket
import json
import time
import sys
from collections import Counter

class WordCountClient:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.server_ip = self.config["server_ip"]
        self.server_port = self.config["server_port"]
        self.k = self.config["k"]
        self.p = self.config["p"]

    def request_chunk(self, offset, count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_ip, self.server_port))
            request = f"{offset},{count}\n"
            sock.sendall(request.encode("utf-8"))
            response = sock.recv(4096).decode("utf-8").strip()
            sock.close()
            return response
        except Exception as e:
            print(f"Socket error: {e}")
            return ""

    def download_and_count(self):
        start = time.time()
        all_words = []
        offset = self.p

        while True:
            resp = self.request_chunk(offset, self.k)
            if not resp:
                break
            words = [w for w in resp.split(",") if w]
            if "EOF" in words:
                words = [w for w in words if w != "EOF"]
                all_words.extend(words)
                break
            all_words.extend(words)
            offset += len(words)
            if len(words) < self.k:
                break

        elapsed_ms = int((time.time() - start) * 1000)
        counts = Counter(all_words)
        return elapsed_ms, counts, len(all_words)

def main():
    client = WordCountClient()
    elapsed_ms, counts, total = client.download_and_count()

    if "--time-only" in sys.argv:
        print(f"ELAPSED_MS:{elapsed_ms}")
    else:
        print(f"ELAPSED_MS:{elapsed_ms}")
        print(f"Total words: {total}")
        for w, c in sorted(counts.items()):
            print(f"{w}, {c}")

if __name__ == "__main__":
    main()
