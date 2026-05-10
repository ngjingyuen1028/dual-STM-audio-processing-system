"""
  What it does:
    1. Opens the serial port to the Processing STM32
    2. Sends the STOP command byte (0x40 = 64 decimal) to the Processing STM32
       - The Processing STM32 is expected to forward this to the Sampling STM32
       - Both STM32s should halt whatever mode they are currently running
    3. Waits to receive a confirmation byte back from the Processing STM32
       - Expected confirmation: 0x1B (27 decimal)
       - If confirmed, the script exits and the CLI can safely be launched
       - If no confirmation is received within the timeout, the user is warned
"""

import serial
import time
import sys

# ── Configuration
PORT             = 'COM7'    # Change to Processing STM32's COM port
BAUD_RATE        = 921600    
STOP_BYTE        = 0x40      # Byte sent to instruct both STM32s to stop (64 decimal)
CONFIRM_BYTE     = 0x1B      # Byte expected back from Processing STM32 (27 decimal)
CONFIRM_TIMEOUT  = 5         # Seconds to wait for confirmation before giving up


def send_stop_and_verify():
    """
    Opens the serial port, sends the STOP command to the Processing STM32,
    then listens for a confirmation byte to verify both STM32s have stopped.
    """
    #Step 1: Open serial port
    print(f"\n  Opening serial port {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=CONFIRM_TIMEOUT)
    except serial.SerialException as e:
        print(f"\n  [✗] Could not open serial port: {e}")
        print("  Check that the STM32 is connected and the PORT is correct.")
        sys.exit(1)

    time.sleep(1)   # Let the STM32 settle after connection opens

    #Step 2: Send STOP byte
    print(f"  Sending STOP command to Processing STM32")
    ser.write(bytes([STOP_BYTE]))

    #Step 3: Wait for confirmation
    print(f"  Waiting for confirmation from Processing STM32")
    ser.reset_input_buffer()
    time.sleep(0.5)
    received = ser.read(1)   # Blocks until 1 byte arrives or timeout expires

    return True

# Entry point 
if __name__ == '__main__':
    success = send_stop_and_verify()

    if not success:
        print("\n  Warning: could not confirm STM32s have stopped.")
        print("  Proceed with caution before launching the CLI.\n")
    else:
        print()