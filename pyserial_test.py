import wave
import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from manual_mode import send_manual_and_verify
from stopstm import send_stop_and_verify

# Config
PORT        = 'COM7'        # Change to your Processing STM32's COM port
BAUD_RATE   = 115200        # Must match the STM32's UART baud rate
SAMPLE_RATE = 10000          # Hz — must be >= 5000 (5 ksps). 8000 Hz is standard audio.
OUTPUT_FILE = 'audio/task2.wav' # Change to WHEREVER YOU WANT
TEAM_ID = 'J08'
COMFIRM_BYTE = 0x1B
CONFIRM_TIMEOUT = 5
MANUAL_BYTE = 0x11
STOP_BYTE = 0x40


def record(duration_s):
    total_samples = SAMPLE_RATE * duration_s  # Total number of bytes to read
    
    print(f"Recording {duration_s}s of audio at {SAMPLE_RATE} sps ({total_samples} samples)...") #some random shi to make sure code is running
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


def get_output_filename(duration_s):
    # Build a filename containing team ID, sample rate, duration, and timestamp.
    # Example: J08_2_8000sps_5s_20260430_142301.wav
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{TEAM_ID}_{SAMPLE_RATE}sps_{int(duration_s)}s_{timestamp}."

def save_wav(data, duration_s):
    #Write WAV file
    filename = get_output_filename(duration_s)
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(1)           # Mono
        wf.setsampwidth(1)           # 8-bit samples = 1 byte per sample
        wf.setframerate(SAMPLE_RATE) # Sample rate in Hz
        wf.writeframes(data.tobytes())
    
        print(f"Audio saved to '{OUTPUT_FILE}' ({len(data)} samples, {duration_s}s")

def save_plot(data, duration_s):
    filename = get_output_filename(duration_s, 'png')
 
    # Build a time axis in seconds (one point per sample)
    time_axis = np.linspace(0, len(data) / SAMPLE_RATE, num=len(data))
 
    plt.figure(figsize=(12, 4))
    plt.plot(time_axis, data, linewidth=0.5, color='steelblue')
    plt.title(
        f'Audio Waveform — Team {TEAM_ID}\n'
        f'Sample Rate: {SAMPLE_RATE} Hz | Duration: {int(duration_s)}s',
        fontsize=13
    )
    plt.xlabel('Time (s)', fontsize=11)
    plt.ylabel('Amplitude (0–255)', fontsize=11)
    plt.xlim([0, time_axis[-1]])
    plt.ylim([0, 255])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"  [✓] Waveform plot saved: {filename}")

def save_csv(data, duration_s):
    filename = get_output_filename(duration_s, 'csv')

    df = pd.DataFrame(data, colums=['sample_value'])
    df.to_csv(filename, index=False)

    with open(filename, 'r') as f:
        og = f.read()
    with open(filename, 'w') as f:
        f.write(f'Sample Rate: {SAMPLE_RATE} Hz\n' + og)
    print(f"  [✓] CSV file saved: {filename}")

def prompt_output_format():
    print("\n  What format would you like to save?")
    print("  Enter one or more numbers separated by spaces (e.g. '1 2').")
    print("  ─────────────────────────────")
    print("  [1] WAV file")
    print("  [2] PNG waveform plot")
    print("  [3] CSV file")
    print("  [0] Discard recording — do not save anything")
    print("  ─────────────────────────────")
 
    valid = {'0', '1', '2', '3'}
 
    while True:
        raw = input("\n  Enter your choice(s): ").strip()
        choices = set(raw.split())   # split on spaces, deduplicate
 
        if not choices.issubset(valid):
            print("  Invalid input. Only use 0, 1, 2, or 3 separated by spaces.")
            continue
        if '0' in choices and len(choices) > 1:
            print("  Cannot combine [0] with other options. Enter 0 alone to discard.")
            continue
        return choices

def manual_recording_mode():

    print("\n" + "─" * 60)
    print("  MANUAL RECORDING MODE")
    print("─" * 60)
    print("  Enter how long you want to record for.")
    print("─" * 60)
 
    # Signal both STM32s to enter Manual Recording Mode and wait for confirmation
    confirmed = send_manual_and_verify()
    if not confirmed:
        print("\n  [✗] Could not confirm STM32s are ready. Returning to main menu.")
        return
 
    # Get duration from user
    while True:
        try:
            duration_input = input("\n  Enter recording duration in seconds (e.g. 5): ")
            duration_s = float(duration_input)
            if duration_s <= 0:
                print("  Please enter a positive number.")
                continue
            break
        except ValueError:
            print("  Invalid input. Please enter a number (e.g. 5 or 2.5).")
 
    # Record and save
    data = record(int(duration_s))
    
    choices = prompt_output_format()
 
    if '0' in choices or not choices:
        print("\n  Recording discarded. Returning to main menu.")
        return
 
    if '1' in choices:
        save_wav(data, int(duration_s))
    if '2' in choices:
        save_plot(data, int(duration_s))
    if '3' in choices:
        save_csv(data, int(duration_s))
 
    print("\n  Returning to main menu.")

def main_menu():
    """Display the main menu and route to the selected mode."""
    send_stop_and_verify()

    while True:
        print("\n  MAIN MENU")
        print("  ─────────────────────────────")
        print("  [1] Manual Recording Mode")
        print("  [0] Exit")
        print("  ─────────────────────────────")
 
        choice = input("\n  Enter your choice: ").strip()
 
        if choice == '1':
            manual_recording_mode()
        elif choice == '0':
            print("\n  Exiting. Goodbye!\n")
            break
        else:
            print("  Invalid input. Please enter 1 or 0.")
 
# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    main_menu()