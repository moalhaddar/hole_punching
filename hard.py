import socket
import random
import threading
import sys
import select
import time

ping_received = threading.Event()

def listen_and_respond(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    print(f"Listening on port {port}")
    
    while not ping_received.is_set():
        ready = select.select([sock], [], [], 1)
        if ready[0]:
            data, addr = sock.recvfrom(1024)
            if data.decode('utf-8') == 'ping':
                print(f"Received ping from {addr}")
                sock.sendto(b'pong', addr)
                print(f"Sent pong to {addr}")
                ping_received.set()
                
                while True:
                    ready = select.select([sock], [], [], 5)
                    if ready[0]:
                        data, _ = sock.recvfrom(1024)
                        if data.decode('utf-8') == 'ping':
                            print(f"Received ping on port {port}")
                            sock.sendto(b'pong', addr)
                            print(f"Sent pong response on port {port}")
                        else:
                            print(f"Received unexpected data on port {port}: {data.decode('utf-8')}")
                    else:
                        print(f"No ping received on port {port}")

                    time.sleep(1)
    
    if not ping_received.is_set():
        sock.close()

def main():
    ports = random.sample(range(1001, 65536), 256)
    threads = []
    
    for port in ports:
        thread = threading.Thread(target=listen_and_respond, args=(port,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()