import socket
import random
import threading
import sys
import select
import time

pong_received = threading.Event()
tried_ports = set()
ports_lock = threading.Lock()

def try_port(target_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        while not pong_received.is_set():
            sock.sendto(b'ping', (target_ip, port))
            print(f"Sent ping to {target_ip}:{port}")
            
            ready = select.select([sock], [], [], 1)
            if ready[0]:
                data, addr = sock.recvfrom(1024)
                if data.decode('utf-8') == 'pong':
                    print(f"Received pong from {addr}")
                    pong_received.set()
                    
                    while True:
                        sock.sendto(b'ping', addr)
                        print(f"Keeping connection alive on port {port}")
                        ready = select.select([sock], [], [], 5)
                        if ready[0]:
                            data, _ = sock.recvfrom(1024)
                            if data.decode('utf-8') == 'pong':
                                print(f"Received pong response on port {port}")
                            else:
                                print(f"Received unexpected data on port {port}: {data.decode('utf-8')}")
                        else:
                            print(f"No response received on port {port}")
                        
                        time.sleep(1)
                
    except Exception as e:
        print(f"Error on port {port}: {e}")
    finally:
        if not pong_received.is_set():
            sock.close()

def get_untried_ports(count):
    with ports_lock:
        available_ports = set(range(1001, 65536)) - tried_ports
        if len(available_ports) < count:
            print("Warning: All ports have been tried. Resetting tried_ports.")
            tried_ports.clear()
            available_ports = set(range(1001, 65536))
        
        selected_ports = random.sample(list(available_ports), min(count, len(available_ports)))
        tried_ports.update(selected_ports)
        return selected_ports

def main(target_ip):
    while not pong_received.is_set():
        untried_ports = get_untried_ports(1000)
        threads = []
        for port in untried_ports:
            thread = threading.Thread(target=try_port, args=(target_ip, port))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join(timeout=1)
            if pong_received.is_set():
                break
        
        if not pong_received.is_set():
            print("No pong received in this batch. Trying next batch.")

    print("Pong received. Stopping search for other ports.")
    
    for thread in threads:
        if thread.is_alive():
            thread.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python easy.py <target_ip>")
        sys.exit(1)
    main(sys.argv[1])