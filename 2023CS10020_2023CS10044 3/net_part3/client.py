#!/usr/bin/env python3
import time
import argparse
import socket
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, required=True)
    parser.add_argument("--client-id", type=str, required=True)
    parser.add_argument("--server-ip", type=str, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    start_time = time.time()

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((args.server_ip, args.port))

        for _ in range(args.batch_size):
            s.sendall(b"GET 5\n")
            data = s.recv(1024)

        s.close()
    except Exception as e:
        print(f"Client {args.client_id} error: {e}")

    completion_time = time.time() - start_time

    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{args.client_id}.log", "w") as f:
        f.write(f"{args.client_id},{completion_time}\n")

    print(f"Client {args.client_id} finished in {completion_time:.2f} seconds")
