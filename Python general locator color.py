import cv2
import numpy as np
import socket

# --- CONFIGURATION ---
ROBOT_IP = "192.168.1.50" # Ensure this matches your robot's IP
UDP_PORT = 4210
TOWER_1_URL = "http://192.168.1.101:8080" # Fixed Port from 81 to 8080
TOWER_2_URL = "http://192.168.1.102:8080"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_green_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Calibrated green range for better detection
    lower_green = np.array([35, 100, 40])
    upper_green = np.array([85, 255, 255])
    return cv2.inRange(hsv, lower_green, upper_green)

cap1 = cv2.VideoCapture(TOWER_1_URL)
cap2 = cv2.VideoCapture(TOWER_2_URL)

print("Project ARC: Python Brain Active...")

while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    
    if ret1:
        mask1 = get_green_mask(frame1)
        # Fixed logic: 1M pixels was impossible. 8000 is ~10% of frame.
        if np.sum(mask1) > 8000: 
            print("Tower 1: Target Found! Signaling Robot...")
            sock.sendto(b'F', (ROBOT_IP, UDP_PORT))

    if ret2:
        mask2 = get_green_mask(frame2)
        if np.sum(mask2) > 8000:
            print("ERROR: Target on Tower 2 side. System restricted.")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap1.release()
cv2.destroyAllWindows()
