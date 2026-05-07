import wave
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os



PORT        = 'COM7'        # Change to your Processing STM32's COM port
BAUD_RATE   = 921600        # Must match the STM32's UART baud rate
SAMPLE_RATE = 10000          # Hz — must be >= 5000 (5 ksps). 8000 Hz is standard audio.
TEAM_ID = 'J08'

def get_output_folder(duration_s):
    # Build a filename containing team ID, sample rate, duration, and timestamp.
    # Example: J08_2_8000sps_5s_20260430_142301.wav
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    return f"{TEAM_ID}_{SAMPLE_RATE}sps_{int(duration_s)}s_{timestamp}/"

def save_wav(data, duration_s):
    folder = "outputs/" + get_output_folder(duration_s)
    os.makedirs(folder, exist_ok=True)
    filename = folder + "/audio.wav"
    #Write WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)           # Mono
        wf.setsampwidth(1)           # 8-bit samples = 1 byte per sample
        wf.setframerate(SAMPLE_RATE) # Sample rate in Hz
        wf.writeframes(data.tobytes())
    
        print(f"Audio saved to '{filename}' ({len(data)} samples, {duration_s}s")

def save_plot(data, duration_s):
    folder = "outputs/" + get_output_folder(duration_s)
    os.makedirs(folder, exist_ok=True)
    filename = folder + "/plot.png"
 
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
    plt.ylim([0,256])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"  [✓] Waveform plot saved: {filename}")

def save_csv(data, duration_s):
    folder = "outputs/" + get_output_folder(duration_s)
    os.makedirs(folder, exist_ok=True)
    filename = folder + "/rawdata.csv"
    header_df = pd.DataFrame([SAMPLE_RATE], columns=['samples'])
    samples_df = pd.DataFrame(data, columns=['samples'])
    whole_df = pd.concat([header_df, samples_df], ignore_index=True)

    whole_df.to_csv(filename, index=False)

    with open(filename, 'r') as f:
        og = f.read()
    with open(filename, 'w') as f:
        f.write(f'Sample Rate: {SAMPLE_RATE} Hz\n' + og)
    print(f"  [✓] CSV file saved: {filename}\n")
    print("Saved csv file to:", os.path.abspath(filename))
    print('\n')

def prompt_output_format():
    print("\n  What format would you like to save?")
    print("  Enter one or more numbers separated by spaces (e.g. '1 2 3').")
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