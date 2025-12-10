import pandas as pd
import numpy as np
import os

dir_path = "./Final Project/Data"
all_files = [file_name for file_name in os.listdir(dir_path)]
data = pd.DataFrame()

for file in all_files:
    full_path = os.path.join(dir_path, file)
    file_data = pd.read_csv(full_path, sep='|')
    file_data['Date'] = file[-10:-4]
    data = pd.concat([data, file_data])

data = data.sort_values(by='Date')
data.to_csv(dir_path + '/METLN_data.csv', index=False)
