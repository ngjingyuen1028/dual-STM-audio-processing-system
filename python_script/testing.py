import wave
import serial
import serial.tools.list_ports
import time
import numpy as np
 
# Config
PORT        = 'COM7'        # Change to your Processing STM32's COM port
BAUD_RATE   = 115200        # Must match the STM32's UART baud rate
SAMPLE_RATE = 10000          # Hz — must be >= 5000 (5 ksps). 8000 Hz is standard audio.
DURATION_S  = 5             # Hard-coded recording length in seconds (PLEASE CHANGE TO MATCH AUDIO FILE)


ser = serial.Serial(PORT, BAUD_RATE)

head = ser.read(1)
print(head.decode())

