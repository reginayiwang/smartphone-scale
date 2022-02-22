import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def segment_data(df):
    # Separate pre load (0-3 sec) and with load (5-8 sec)
    pre_load = df[(df['Time (s)'] <= 3)]
    with_load = df[(df['Time (s)'] >= 5) & (df['Time (s)'] <= 8)]
    return pre_load['y'], with_load['y']

def calc_intensity(arr):
    intensity = 1 / len(arr) * np.sum(abs(arr - np.mean(arr)))
    return intensity

def relative_intensity(pre_load, with_load):
    pre_arr, with_arr = np.asarray(pre_load), np.asarray(with_load)
    pre_intensity, with_intensity = calc_intensity(pre_arr), calc_intensity(with_arr)
    return pre_intensity - with_intensity

def process_data(samples):
    intensities = []
    for i in range(samples):
        df = pd.read_csv(f"./data/accelerometer/accelerometer_{i}.csv")
        # plt.title(f"Raw Data: accelerometer_{i}.csv")
        # plt.plot(df['Time (s)'], df['y'])
        # plt.show()
        pre_load, with_load = segment_data(df)
        
        intensity = relative_intensity(pre_load, with_load)
        intensities.append([i, intensity])

    intensity_df = pd.DataFrame(intensities, columns=['ID', 'Intensity'])
    weight_df = pd.read_csv('./data/weights.csv')
    merged_df = weight_df.merge(intensity_df, on='ID')

    # plt.scatter(x=merged_df['Weight (g)'], y=merged_df['Intensity'])
    # plt.show()
    merged_df.to_csv('./data/data.csv', index=False)

if len(sys.argv) == 2:
    process_data(int(sys.argv[1]))
else:
    print("Provide number of samples: python preprocess.py [num]")