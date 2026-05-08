import wave
import serial
import serial.tools.list_ports
import time
import numpy as np
 
# Config
PORT        = 'COM7'        # Change to your Processing STM32's COM port
BAUD_RATE   = 921600        # Must match the STM32's UART baud rate
SAMPLE_RATE = 22050          # Hz — must be >= 5000 (5 ksps). 8000 Hz is standard audio.
DURATION_S  = 10             # Hard-coded recording length in seconds (PLEASE CHANGE TO MATCH AUDIO FILE)
OUTPUT_FILE = 'audio/task1.wav' # Change to WHEREVER YOU WANT



ser = serial.Serial(PORT, BAUD_RATE)

ser.write(b'\x40')
print("Stopping of the STM")

ser.reset_input_buffer()
while True:
    confirmation = ser.read(1)
    print(confirmation[0])  # prints 27
    if confirmation[0] == 27:
        break

print("All stm stops properly")

hold = input("Please enter :")
ser.write(b'\x11')
print("sending instruction mode")

while True:
    confirmation = ser.read(1)
    print(confirmation[0])  # prints 27
    if confirmation[0] == 27:
        break

hold = input("Please enter to start :")
ser.write(b'\x04')

total_samples = SAMPLE_RATE * DURATION_S
data = []
 
while len(data) < total_samples:
    byte = ser.read(1)          # Blocks until 1 byte is received (up to timeout)
    if len(byte) == 0:
        print("Warning: timeout waiting for data. Is the STM32 sending?")
        continue
    data.append(byte[0])        # byte[0] is the uint8 sample value (0–255)
 
ser.close()
print("Sampling done. Serial port closed.")
 
# ── Convert to numpy array ───────────────────────────────────────────────────
# The Processing STM32 has already applied the moving average filter.
# Samples arrive as raw 8-bit unsigned integers (0–255).
# No re-normalization needed — just cast directly to uint8.
data = np.array(data)
# data = (data - data.min()) / data.max()  # scale to 0-1
# data = data * 255                         # scale to 0-255
data = data.astype(np.uint8)             # convert to uint8
 
# ── Write WAV file ───────────────────────────────────────────────────────────
with wave.open(OUTPUT_FILE, 'wb') as wf:
    wf.setnchannels(1)           # Mono
    wf.setsampwidth(1)           # 8-bit samples = 1 byte per sample
    wf.setframerate(SAMPLE_RATE) # Sample rate in Hz
    wf.writeframes(data.tobytes())
 
print(f"Audio saved to '{OUTPUT_FILE}' ({len(data)} samples, {DURATION_S}s @ {SAMPLE_RATE} Hz)")

ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device, port.description)
hold = input("Please enter to start :")


ser.write(b'\x40')
print("Stopping of the STM")