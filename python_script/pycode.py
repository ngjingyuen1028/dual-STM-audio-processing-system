import wave
import serial
import time
import numpy as np
 
# Configuration
PORT        = 'COM7'        # Change to Processing STM32's COM port
BAUD_RATE   = 921600        # STM32's UART baud rate
SAMPLE_RATE = 22050       
DURATION_S  = 10             
OUTPUT_FILE = 'audio/task1.wav' # Change to WHEREVER YOU WANT
#--

total_samples = SAMPLE_RATE * DURATION_S  # Total number of bytes to read
 
print(f"Recording {DURATION_S}s of audio at {SAMPLE_RATE} sps ({total_samples} samples)...") #some random shi to make sure code is running
print(f"Opening serial port {PORT} at {BAUD_RATE} baud...") #same here
 
ser = serial.Serial(PORT, BAUD_RATE)
time.sleep(0.2)  # Allow STM32 to settle after serial connection opens
 
data = []
 
while len(data) < total_samples:
    byte = ser.read(1)          # Blocks until 1 byte is received (up to timeout)
    if len(byte) == 0:
        print("Warning: timeout waiting for data. Is the STM32 sending?")
        continue
    data.append(byte[0])        # byte[0] is the uint8 sample value (0–255)
 
ser.close()
print("Sampling done. Serial port closed.")
 
# Convert to numpy array 
data = np.array(data)
# data = (data - data.min()) / data.max()  # scale to 0-1
# data = data * 255                         # scale to 0-255
data = data.astype(np.uint8)             # convert to uint8
 
# Write WAV file
with wave.open(OUTPUT_FILE, 'wb') as wf:
    wf.setnchannels(1)           # Mono
    wf.setsampwidth(1)           # 8-bit samples = 1 byte per sample
    wf.setframerate(SAMPLE_RATE) # Sample rate in Hz
    wf.writeframes(data.tobytes())
 
print(f"Audio saved to '{OUTPUT_FILE}' ({len(data)} samples, {DURATION_S}s @ {SAMPLE_RATE} Hz)")