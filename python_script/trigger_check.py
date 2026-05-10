import serial
import time
import sys
 
# Configuration 
PORT             = 'COM7'    # Change to Processing STM32's COM port
BAUD_RATE        = 921600
TRIGGER_BYTE      = 0x22      # Byte sent to instruct both STM32s to enter  Trigger Mode (18 decimal)
CONFIRM_BYTE     = 0x1B      # Byte expected back from Processing STM32 (27 decimal)
CONFIRM_TIMEOUT  = 5         # Seconds to wait for confirmation before giving up
 
def send_trigger_and_verify():
    # Step 1: Open serial port
    print(f"\n  Opening serial port {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=CONFIRM_TIMEOUT)
    except serial.SerialException as e:
        print(f"\n  [✗] Could not open serial port: {e}")
        print("  Check that the STM32 is connected and the PORT is correct.")
        sys.exit()
 
    time.sleep(1)   # Let the STM32 settle after connection opens
 
    # Step 2: Send TRIGGER RECORDING byte
    print(f"  Sending DISTNACE TRIGGER RECORDING command to Processing STM32...")
    ser.write(bytes([TRIGGER_BYTE]))
    received = ser.read(1)  
 
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