import cv2
import numpy as np
import socket

# --- CONFIGURATION ---
ROBOT_IP = "192.168.1.50" 
UDP_PORT = 4210
TOWER_1_URL = "http://192.168.1.101:81/stream"
TOWER_2_URL = "http://192.168.1.102:81/stream"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_green_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
        if np.sum(mask1) > 1000000: # Threshold for detection
            print("Tower 1: Target Found! Signaling Robot...")
            sock.sendto(b'F', (ROBOT_IP, UDP_PORT))

    if ret2:
        mask2 = get_green_mask(frame2)
        if np.sum(mask2) > 1000000:
            print("ERROR: Target on Tower 2 side. System restricted.")

    # Note: No cv2.imshow here to save PC processing power 
    # since you are using the HTML Dashboard instead!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap1.release()
