#include <MatrixMini.h>
#include <WiFi.h>
#include <Wire.h>

const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";
WiFiUDP udp;

enum State { IDLE, MOVE_10CM, LOCAL_SEARCH, FINISHED };
State robotState = IDLE;

void setup() {
  Mini.begin();
  Mini.imu.begin();
  Wire.begin(); 
  
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  // Print IP so you can put it in the Python script
  Serial.println("\nRobot Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP()); 

  udp.begin(4210);
  delay(2000); // Calibration time for IMU [cite: 7]
}

void loop() {
  switch (robotState) {
    case IDLE:
      // Wait for 'F' trigger from PC [cite: 7]
      if (udp.parsePacket() && udp.read() == 'F') {
        robotState = MOVE_10CM;
      }
      break;

    case MOVE_10CM:
      driveStraight(50, 1200); // 1.2 seconds of movement [cite: 8]
      robotState = LOCAL_SEARCH;
      break;

    case LOCAL_SEARCH:
      Wire.requestFrom(0x12, 2); // Request data from Camera [cite: 10]
      if (Wire.available() >= 2) {
        int cx = (Wire.read() << 8) | Wire.read();
        
        if (cx == 0) return; // Ignore if no target
        
        if (cx < 140) { // Steer Left [cite: 11]
          Mini.M1.set(20); Mini.M2.set(20);
          Mini.M3.set(40); Mini.M4.set(40);
        } else if (cx > 180) { // Steer Right [cite: 12]
          Mini.M1.set(40); Mini.M2.set(40);
          Mini.M3.set(20); Mini.M4.set(20);
        } else { // Centered [cite: 13]
          robotState = FINISHED;
        }
      }
      break;

    case FINISHED:
      Mini.M1.set(0); Mini.M2.set(0); Mini.M3.set(0); Mini.M4.set(0);
      break;
  }
}

void driveStraight(int speed, int duration) {
  long start = millis();
  float target = Mini.imu.getAngleZ(); // Lock current heading [cite: 16]
  while (millis() - start < duration) {
    float error = target - Mini.imu.getAngleZ();
    int corr = (int)(error * 2.5); // Gyro correction [cite: 18]
    Mini.M1.set(speed + corr); Mini.M2.set(speed + corr);
    Mini.M3.set(speed - corr); Mini.M4.set(speed - corr);
  }
}
