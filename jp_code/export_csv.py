import pandas as pd
import os

data = {'Name': ['Alice', 'Bob'], 'Age': [25, 30]}
df = pd.DataFrame(data)

filename = 'test.csv'

df.to_csv('test.csv', index=False)
print("Saved csv file to:", os.path.abspath(filename))
