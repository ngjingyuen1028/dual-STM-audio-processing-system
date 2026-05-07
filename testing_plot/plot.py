import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt

data = np.genfromtxt("outputs/csv_files/J08_44100sps_10s_20260506_184937.csv", delimiter = ',', dtype = float, encoding = 'utf-8', skip_header=3)
filtered_data = medfilt(data, kernel_size=3)
print(data)


fig, ax = plt.subplots(figsize = (8,5))
ax.plot(np.arange(1,len(filtered_data) + 1,1), filtered_data)

plt.show()