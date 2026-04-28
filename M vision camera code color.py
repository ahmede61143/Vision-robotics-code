import sensor, image, time, network, usocket
from pyb import I2C

# 1. Setup I2C & Camera
# Acts as Slave (addr 0x12) for the Matrix Mini [cite: 1, 10]
bus = I2C(2, I2C.SLAVE, addr=0x12)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA) # 320x240 resolution
sensor.skip_frames(time = 2000)

# 2. Setup WiFi for Streaming
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Your_WiFi_SSID", "Your_WiFi_Password") # UPDATE THESE

server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server.bind(('', 8080)) # PC Brain connects to this port [cite: 2]
server.listen(1)
server.settimeout(0.1)

green_threshold = (30, 100, -80, -10, 0, 80)
cx = 0 

while(True):
    img = sensor.snapshot()
    blobs = img.find_blobs([green_threshold])
    
    if blobs:
        largest = max(blobs, key=lambda b: b.pixels())
        img.draw_rectangle(largest.rect())
        cx = largest.cx()
        # Provide data to Matrix over I2C [cite: 2]
        try:
            bus.send(bytes([cx >> 8, cx & 0xFF]))
        except: pass

    # Check for PC Brain Dashboard connection [cite: 3]
    try:
        client, addr = server.accept()
        client.send("HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n")
        img_buf = img.compress(quality=70).to_bytes()
        client.send("--frame\r\nContent-Type: image/jpeg\r\n\r\n" + img_buf + "\r\n")
        client.close()
    except: pass
