import sys
import os
from glob import glob
sys.path.append(os.path.join(os.path.dirname(__file__)))
from c_video_preprocessing import main as c_video_preprocessing
from e_calibration import main as e_calibration
from g_auto_piv import main as g_auto_piv
from h_postprocessing import main as h_postprocessing
from i_suggest_FrameInterval import main as i_suggest_FrameInterval

project_dir_path = r'F:\3DPIV-2022\project'
json_lsit = glob(os.path.join(project_dir_path, 'project*', 'system', 'control_dict.json'))
failed_list = []
for json_path in json_lsit:
    print(json_path)
    print('失敗したやつ')
    print(failed_list)
    try:
        c_video_preprocessing(json_path, frame_interval=20)
        e_calibration(json_path)
        g_auto_piv(json_path, inner_len=32, outer_len=52, interval=16)
        h_postprocessing(json_path)
        c_video_preprocessing(json_path, frame_interval=i_suggest_FrameInterval(json_path, 8))
        e_calibration(json_path)
        g_auto_piv(json_path, inner_len=32, outer_len=52, interval=16)
        h_postprocessing(json_path)
    except:
        failed_list.append(json_path)

print('失敗したプロジェクトディレクトリ')
for failed in failed_list:
    print(failed)