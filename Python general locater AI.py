import socket

# Network Configuration
TOWER_IP = "192.168.1.10" # ESP32 Tower
ROVER_IP = "192.168.1.20" # Matrix Mini
PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

print("System Online. Waiting for Tower detection...")

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode()

    # If Tower ESPs see the artifact
    if "DETECTED" in message:
        print(f"Tower Signal: {message}")
        # Tell Rover to start searching locally
        sock.sendto("SEARCH".encode(), (ROVER_IP, PORT))
    
    time.sleep(0.1)
