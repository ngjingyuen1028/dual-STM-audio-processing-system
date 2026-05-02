"""
  What it does:
    1. Opens the serial port to the Processing STM32
    2. Sends the MANUAL RECORDING command byte (0x11 = 17 decimal) to the Processing STM32
       - The Processing STM32 is expected to forward this to the Sampling STM32
       - Both STM32s should enter Manual Recording Mode
    3. Waits to receive a confirmation byte back from the Processing STM32
       - Expected confirmation: 0x1B (27 decimal)
       - If confirmed, the function returns True and recording can begin
       - If no confirmation is received within the timeout, the user is warned
"""
 
import serial
import time
 
# ── Configuration ─────────────────────────────────────────────────────────────
PORT             = 'COM3'    # Change to your Processing STM32's COM port
BAUD_RATE        = 115200
MANUAL_BYTE      = 0x11      # Byte sent to instruct both STM32s to enter Manual Recording Mode (1 decimal)
CONFIRM_BYTE     = 0x1B      # Byte expected back from Processing STM32 (28 decimal)
CONFIRM_TIMEOUT  = 5         # Seconds to wait for confirmation before giving up
# ─────────────────────────────────────────────────────────────────────────────
 
 
def send_manual_and_verify():
    # Step 1: Open serial port
    print(f"\n  Opening serial port {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=CONFIRM_TIMEOUT)
    except serial.SerialException as e:
        print(f"\n  [✗] Could not open serial port: {e}")
        print("  Check that the STM32 is connected and the PORT is correct.")
        return False
 
    time.sleep(1)   # Let the STM32 settle after connection opens
 
    # Step 2: Send MANUAL RECORDING byte
    print(f"  Sending MANUAL RECORDING command to Processing STM32...")
    ser.write(bytes([MANUAL_BYTE]))
    received = ser.read(1)   # Blocks until 1 byte arrives or timeout expires
 
    if len(received) == 0:
        # No byte received within the timeout window
        print("\n  [✗] No confirmation received — timeout expired.")
        print("  The STM32 may not have responded.")
        ser.close()
        return False
 
    received_byte = received[0]
 
    if received_byte == CONFIRM_BYTE:
        # Correct confirmation byte received
        print(f"\n  [✓] Confirmation received — both STM32s are in Manual Recording Mode.")
        ser.close()
        return True
    else:
        # An unexpected byte came back
        print(f"\n  [!] Unexpected byte received: 0x{received_byte:02X}")
        ser.close()
        return False