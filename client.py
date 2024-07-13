import socket
import random
import threading
import time

# Global flag to indicate if a pong has been received
pong_received = threading.Event()

# Set to keep track of tried ports
tried_ports = set()
ports_lock = threading.Lock()

def try_port(target_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    
    try:
        while not pong_received.is_set():
            sock.sendto(b'ping', (target_ip, port))
            print(f"Sent ping to port {port}")
            
            try:
                data, addr = sock.recvfrom(1024)
                
                if data.decode('utf-8') == 'pong':
                    print(f"Received pong from {addr}")
                    pong_received.set()
                    
                    # Keep this connection alive
                    while True:
                        sock.sendto(b'ping', addr)
                        print(f"Keeping connection alive on port {port}")
                        time.sleep(1)  # Send a ping every 5 seconds
                        
            except socket.timeout:
                print(f"No response from port {port}")
                break  # Exit the while loop if no response
                
    except Exception as e:
        print(f"Error on port {port}: {e}")
    finally:
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

def main():
    target_ip = input("Enter the target IP address: ")
    
    while not pong_received.is_set():
        untried_ports = get_untried_ports(100)
        threads = []
        for port in untried_ports:
            thread = threading.Thread(target=try_port, args=(target_ip, port))
            thread.start()
            threads.append(thread)
        
        # Wait for threads to complete or for a pong to be received
        for thread in threads:
            thread.join(timeout=1)
            if pong_received.is_set():
                break
        
        if not pong_received.is_set():
            time.sleep(1)  # Wait for 1 second before the next batch

    print("Pong received. Stopping search for other ports.")
    
    # Wait for the successful thread to keep the connection alive
    for thread in threads:
        if thread.is_alive():
            thread.join()

if __name__ == "__main__":
    main()