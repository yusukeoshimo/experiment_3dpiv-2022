import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json

def calc_max_displacement(json_path):
    control_dict = read_json(json_path)
    project_dir_path = control_dict['project_dir_path']
    
    side_df = pd.read_csv(os.path.join(project_dir_path, 'side', 'velocity', 'velocity_{}.csv'.format(control_dict['side']['frame_interval'])))
    data_df = side_df.loc[(side_df['data_bool']==True), ['dx', 'dy', 'dz']]
    now_max = data_df.abs().values.max()
    return now_max

def main(json_path, target_displacement):
    control_dict = read_json(json_path)
    now_max = calc_max_displacement(json_path)
    suggest = int(round(control_dict['side']['frame_interval']*(target_displacement/now_max)))
    return suggest

if __name__ == '__main__':
    json_path = input('input json path > ')
    print(main(json_path, 10))