import numpy as np
import wave
import serial
import serial.tools.list_ports

def which_format(format_array, sample_rate, data_array):
    prev_val = []
    for i in range(len(format_array)):
        if format_array[i] in prev_val:
            continue
        
        prev_val.append(format_array[i])

        if format_array[i] == "1":
            print("making wav file")
            wave_make(sample_rate, data_array)
        elif format_array[i] == "2":
            print("making png file")
            # png_make()
        elif format_array[i] == "3":
            print("making csv file")
            # csv_make()


def wave_make(sample_rate, data_array):
    
    with wave.open("audio.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(sample_rate)
        wf.writeframes(data_array.tobytes())



devices = serial.tools.list_ports.comports()

# for device in devices:
#     print(device.device, device.description)

# ser = serial.Serial('COM11', 115200)

data_list = []
sample_rate = 9000


# Inputs
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

print("How long would you like to record for? (seconds)")

while True:
    length_recording = input()
    try:
        length_recording_int = int(length_recording)
        if length_recording_int <= 0:
            print("Error: Integer must be positive. Please input a different value.")
            continue
        break
    except ValueError or TypeError:
        print("Error: Please enter a valid integer.")



print("\nWhich format(s) would you like the audio data to be output as?\n(Please enter the number corresponding to the format. If you would like multiple outputs, please enter the numbers seperated by spaces.\n1. wav file\n2. png file\n3. csv file")

while True:
    formats = input()

    format_array = formats.split()

    if not (1 <= len(format_array) <= 3):
        print("Please enter between 1 and 3 formats that you would like to be output.")
    
    valid = True
    for i in format_array:
        if i not in ["1", "2", "3"]:
            valid = False
            break

    if not all(i in ["1", "2", "3"] for i in format_array):
        print("Error: Please only enter numbers 1, 2, or 3.")
        continue

    break


# Sampling the data
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


for i in range(length_recording_int*sample_rate):
    data = ser.read(1)
    data_list.append(data[0])

data_array = np.array(data_list)

data_array = (data_array - data_array.min()) / data_array.max()
data_array = data_array * 255
data_array = data_array.astype(np.uint8)


# Turning the sampled data into whichever format it has been requested to be in

which_format(format_array, sample_rate, data_array)