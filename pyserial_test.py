import wave
import serial
import time
import numpy as np
 
# Config
PORT        = 'COM3'        # Change to your Processing STM32's COM port
BAUD_RATE   = 115200        # Must match the STM32's UART baud rate
SAMPLE_RATE = 9000          # Hz — must be >= 5000 (5 ksps). 8000 Hz is standard audio.
DURATION_S  = 5             # Hard-coded recording length in seconds (PLEASE CHANGE TO MATCH AUDIO FILE)
OUTPUT_FILE = r'C:\Users\YourName\Desktop\audio_output.wav' # Change to WHEREVER YOU WANT
#--

total_samples = SAMPLE_RATE * DURATION_S  # Total number of bytes to read
 
print(f"Recording {DURATION_S}s of audio at {SAMPLE_RATE} sps ({total_samples} samples)...") #some random shi to make sure code is running
print(f"Opening serial port {PORT} at {BAUD_RATE} baud...") #same here
 
ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
time.sleep(1)  # Allow STM32 to settle after serial connection opens
 
data = []
 
while len(data) < total_samples:
    byte = ser.read(1)          # Blocks until 1 byte is received (up to timeout)
    if len(byte) == 0:
        print("Warning: timeout waiting for data. Is the STM32 sending?")
        continue
    data.append(byte[0])        # byte[0] is the uint8 sample value (0–255)
 
ser.close()
print("Serial port closed.")
 
# ── Convert to numpy array ───────────────────────────────────────────────────
# The Processing STM32 has already applied the moving average filter.
# Samples arrive as raw 8-bit unsigned integers (0–255).
# No re-normalization needed — just cast directly to uint8.
data = np.array(data)
data = (data - data.min()) / data.max()  # scale to 0-1
data = data * 255                         # scale to 0-255
data = data.astype(np.uint8)             # convert to uint8
 
# ── Write WAV file ───────────────────────────────────────────────────────────
with wave.open(OUTPUT_FILE, 'wb') as wf:
    wf.setnchannels(1)           # Mono
    wf.setsampwidth(1)           # 8-bit samples = 1 byte per sample
    wf.setframerate(SAMPLE_RATE) # Sample rate in Hz
    wf.writeframes(data.tobytes())
 
print(f"Audio saved to '{OUTPUT_FILE}' ({len(data)} samples, {DURATION_S}s @ {SAMPLE_RATE} Hz)")