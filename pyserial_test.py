import wave
import serial
import time
import numpy as np
from datetime import datetime

# Config
PORT        = 'COM7'        # Change to your Processing STM32's COM port
BAUD_RATE   = 115200        # Must match the STM32's UART baud rate
SAMPLE_RATE = 10000          # Hz — must be >= 5000 (5 ksps). 8000 Hz is standard audio.
DURATION_S  = 10             # Hard-coded recording length in seconds (PLEASE CHANGE TO MATCH AUDIO FILE)
OUTPUT_FILE = 'audio/task1.wav' # Change to WHEREVER YOU WANT
TEAM_ID = 'J08'
#--

def print_header():
    # Print the welcome banner
    print("=" * 60)
    print("       Audio Capture CLI — Team", TEAM_ID)
    print("=" * 60)
    print(f"  Port:        {PORT}")
    print(f"  Baud Rate:   {BAUD_RATE}")
    print(f"  Sample Rate: {SAMPLE_RATE} Hz")
    print("=" * 60)

def get_output_filename(duration_s):
    # Build a filename containing team ID, sample rate, duration, and timestamp.
    # Example: J08_2_8000sps_5s_20260430_142301.wav
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{TEAM_ID}_{SAMPLE_RATE}sps_{int(duration_s)}s_{timestamp}.wav"


def record(duration_s):
    total_samples = SAMPLE_RATE * duration_s  # Total number of bytes to read
    
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
    print("Receiving. Serial port closed.")
    
    #Convert to numpy array
    data = np.array(data)
    data = data.astype(np.uint8)# convert to uint8
    
    return data         

def save_wav(duration_s):
    #Write WAV file
    filename = get_output_filename(duration_s)
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(1)           # Mono
        wf.setsampwidth(1)           # 8-bit samples = 1 byte per sample
        wf.setframerate(SAMPLE_RATE) # Sample rate in Hz
        wf.writeframes(data.tobytes())
    
    print(f"Audio saved to '{OUTPUT_FILE}' ({len(data)} samples, {DURATION_S}s @ {SAMPLE_RATE} Hz)")