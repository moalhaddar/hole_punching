import socket
import random
import threading

def listen_on_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    print(f"Listening on port {port}")
    
    while True:
        data, addr = sock.recvfrom(1024)
        if data.decode('utf-8') == 'ping':
            sock.sendto(b'pong', addr)
            print(f"Received ping from {addr}, sent pong on port {port}")

def main():
    threads = []
    used_ports = set()
    
    for _ in range(256):
        while True:
            port = random.randint(1001, 65535)
            if port not in used_ports:
                used_ports.add(port)
                break
        
        thread = threading.Thread(target=listen_on_port, args=(port,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()