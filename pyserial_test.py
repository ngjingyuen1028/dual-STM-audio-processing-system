import serial
import time
import numpy as np
from manual_check import send_manual_and_verify
from trigger_check import send_trigger_and_verify
from stopstm import send_stop_and_verify
from formatify import save_csv, save_plot, save_wav, prompt_output_format

# Config
PORT        = 'COM7'        # Change to your Processing STM32's COM port
BAUD_RATE   = 115200        # Must match the STM32's UART baud rate
SAMPLE_RATE = 10000          # Hz — must be >= 5000 (5 ksps). 8000 Hz is standard audio.
OUTPUT_FILE = 'audio/task2.wav' # Change to WHEREVER YOU WANT
TEAM_ID = 'J08'
COMFIRM_BYTE = 0x1B 
CONFIRM_TIMEOUT = 5
MANUAL_BYTE = 0x11
START_BYTE = 0x04
STOP_BYTE = 0x40
APPEND_WINDOW = 1
END_BYTE = 0xFF
END_SEQ_LEN = 4



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

def save_recording(rawdata, choices):
    duration = len(rawdata) / SAMPLE_RATE
    print(f"\n Saved recording for {duration:.1f} seconds.")

    if '1' in choices:
        save_wav(rawdata, duration)
    if '2' in choices:
        save_plot(rawdata, duration)
    if '3' in choices:
        save_csv(rawdata, duration)

def manual_recording_mode():

    print("\n" + "─" * 60)
    print("  MANUAL RECORDING MODE")
    print("─" * 60)
    print("  Enter how long you want to record for.")
    print("─" * 60)
 
    # Signal both STM32s to enter Manual Recording Mode and wait for confirmation
    send_manual_and_verify()

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

    choices = prompt_output_format()

    ser_temp = serial.Serial(PORT, BAUD_RATE)
    ser_temp.write(bytes([START_BYTE]))
    ser_temp.close()

    data = record(int(duration_s))
 
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



def distance_trigger_mode():
    print("\n" + "─" * 60)
    print("  DISTANCE TRIGGER MODE")
    print("─" * 60)
    print(f"  Listening for ultrasonic trigger on {PORT}.")
    print(f"  Press Ctrl+C to stop and return to the main menu.")
    print("─" * 60)   

    send_trigger_and_verify()

    choices = prompt_output_format()

    if '0' in choices or not choices:
        print("\n  Recording discarded. Returning to main menu.")
        return
    
    ser = serial.Serial(PORT, BAUD_RATE, timeout=None)

    cur = [] #accumulate samples for the current file

    end_byte_count = 0 #end byte tracker

    time.sleep(1)

    print("\n Waiting for trigger...")

    try:
        while True:
            byte = ser.read(1)
            value = byte[0]

            #Checking for the last 4 garbage bytes
            if value == END_BYTE:
                end_byte_count += 1
                if end_byte_count == END_SEQ_LEN:
                    print(f" End Signal Received")
                    if cur:
                        save_recording(cur, choices)
                    cur = []
                    end_byte_count = 0
                    print("\n When tf is the next trigger?")

            else: #if there are 3 garbage bytes in a row, it is actually NOT garbage
                if end_byte_count > 0:
                    cur.extend([END_BYTE] * end_byte_count)
                    end_byte_count = 0
                
                if not cur:
                    print(f"SOMETHING IS THERE, RECORDING NOWWWW!")

                cur.append(value)

    except KeyboardInterrupt:
        print("\n  Keyboard Interrupted, saving and exiting.")
        if cur:
            save_recording(cur, choices)
        ser.close()
        return



def main_menu():
    #Display the main menu and route to the selected mode.
    send_stop_and_verify()

    while True:
        print("\n  MAIN MENU")
        print("  ─────────────────────────────")
        print("  [1] Manual Recording Mode")
        print("  [2] Distance Triggering Mode")
        print("  [0] Exit")
        print("  ─────────────────────────────")
 
        choice = input("\n  Enter your choice: ").strip()
 
        if choice == '1':
            manual_recording_mode()
        elif choice == '2':
            distance_trigger_mode()
        elif choice == '0':
            print("\n  Exiting. Goodbye!\n")
            break
        else:
            print("  Invalid input. Please enter 1, 2 or 0.")
 
# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    main_menu()