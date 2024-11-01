# Arduino Motor Scheduler

This application allows you to schedule stepper motor movements for an Arduino over serial communication.

## Requirements

### Python Application
- Python 3.7+
- PySerial
- CustomTkinter
- Schedule

### Arduino
- Arduino board (tested with Arduino Uno)
- Stepper motor
- Stepper motor driver
- ArduinoJson library

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install the ArduinoJson library in your Arduino IDE
   - Open Arduino IDE
   - Go to Tools > Manage Libraries
   - Search for "ArduinoJson"
   - Install version 6.x or later

3. Upload the `motor_controller.ino` sketch to your Arduino

## Hardware Setup

Connect your stepper motor and driver to the Arduino:
- Step pin -> Arduino pin 3
- Direction pin -> Arduino pin 4
- Connect power and ground according to your motor driver's specifications

## Usage

1. Run the Python application:
```bash
python motor_scheduler.py
```

2. In the application:
   - Enter your Arduino's serial port (e.g., COM3 on Windows or /dev/ttyUSB0 on Linux/Mac)
   - Set the baud rate (default 9600)
   - Click "Connect"
   - Add scheduled moves by specifying:
     - Time (HH:MM format)
     - Direction (clockwise/counterclockwise)
     - Number of steps
   - Click "Start Scheduler" to begin executing scheduled moves

## Notes

- The scheduler will run continuously until stopped
- Scheduled moves will repeat daily at the specified times
- Make sure your Arduino is connected before starting the scheduler
- The application uses JSON for communication with the Arduino

## Troubleshooting

1. If you can't connect to the Arduino:
   - Check that the correct port is selected
   - Verify the Arduino is properly connected
   - Make sure no other program is using the serial port

2. If the motor doesn't move:
   - Check your wiring
   - Verify the motor driver is properly powered
   - Check the serial monitor for any error messages