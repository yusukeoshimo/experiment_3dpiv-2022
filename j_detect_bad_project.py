import sys
import os
import numpy as np
import pandas as pd
from glob import glob
sys.path.append(os.path.join(os.path.dirname(__file__)))
from c_video_preprocessing import main as c_video_preprocessing
from e_calibration import main as e_calibration
from g_auto_piv import main as g_auto_piv
from h_postprocessing import main as h_postprocessing
from i_suggest_FrameInterval import main as i_suggest_FrameInterval
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json

project_par_dir_path = r'F:\3DPIV-2022\project'
project_dir_path_list = glob(os.path.join(project_par_dir_path, 'project*'))

a_list = []
for project_dir_path in project_dir_path_list:
    control_dict = read_json(os.path.join(project_dir_path, 'system', 'control_dict.json'))
    a_list.append(control_dict['bottom']['ux_vs_ux_a'])

df = pd.DataFrame([project_dir_path_list, a_list])
df = df.T
df.columns = ['project_dir_path', 'a']

bad_df = df.loc[((df['a']-1).abs()>0.05)]
print(bad_df)