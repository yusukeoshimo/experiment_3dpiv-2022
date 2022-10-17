import sys
import os
from glob import glob
sys.path.append(os.path.join(os.path.dirname(__file__)))
from c_video_preprocessing import main as c_video_preprocessing
from e_calibration import main as e_calibration

frame_interval = 20
project_dir_path = r'F:\3DPIV-2022\project'
json_lsit = glob(os.path.join(project_dir_path, 'project*', 'system', 'control_dict.json'))
for json_path in json_lsit:
    print(json_path)
    c_video_preprocessing(json_path, frame_interval)
    e_calibration(json_path)