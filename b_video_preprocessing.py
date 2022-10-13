import cv2
import shutil
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json
from experiment.LightGBM.func.video2memmap import video2memmap
from experiment.LightGBM.mk_feature import MkFeature
from experiment.classification.classification_per_pulse import main as classification
from util.txt_replacement import extract_txt
from others.intensity_vs_time import main as mk_fig

json_path = input('input json path > ') 
control_dict = read_json(json_path)
project_dir_path = control_dict['project_dir_path']

tmp_video_dir_path = 'C:\\Users\\student\\Desktop\\動画一時保存'

for position in ['side', 'bottom']:
    # 動画をcドライブからfドライブに移動
    print('動画をfドライブに移動中...')
    raw_video_path = os.path.join(project_dir_path, position, '{}.avi'.format(position))
    tmp_video_path = os.path.join(tmp_video_dir_path, '{}.avi'.format(position))
    shutil.copy2(tmp_video_path, raw_video_path)
    
    # 動画のプロパティを記録
    print('動画のプロパティをjsonファイルに書き込み中...')
    cap = cv2.VideoCapture(raw_video_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    codec = int(cap.get(cv2.CAP_PROP_FOURCC)).to_bytes(4, 'little').decode('utf-8')
    cap.release()
    control_dict[position]['raw_video_w'] = w
    control_dict[position]['raw_video_h'] = h
    control_dict[position]['raw_video_fps'] = fps
    control_dict[position]['raw_video_frame'] = frame_num
    control_dict[position]['raw_video_codec'] = codec
    
    # 動画をmemmapに変換
    print('動画をmemmapに変換中...')
    video_memmap_path = os.path.join(project_dir_path, position, 'video.npy')
    video2memmap(raw_video_path, video_memmap_path)
    
    # 特徴量を生成
    print('特徴量を生成中...')
    mkf = MkFeature()
    feature_memmap_path = os.path.join(project_dir_path, position, 'feature.npy')
    mkf.main(feature_memmap_path, video_memmap_path, w, h)
    control_dict['feature_size'] = mkf.feature_num
    
    # LightGBMで分類
    print('LightGBMで分類中...')
    classified_mmp_dir = os.path.join(project_dir_path, position, 'memmap')
    model_path = os.path.join(project_dir_path, position, 'LightGBM', 'my_LightGBM.pkl')
    pulse_order = control_dict[position]['pulse_order']
    arduino_path = 'F:\\3DPIV-2022\\src\\laser_blinking\\laser_blinking.ino'
    with open(arduino_path) as f:
        txt = f.read()
    cooldown_time = int(extract_txt(txt, 'int cooldown_time = ', ';')[0])/1000
    turn_on_time = int(extract_txt(txt, 'int turn_on_time = ', ';')[0])/1000
    classification(classified_mmp_dir, model_path, feature_memmap_path, mkf.feature_num, video_memmap_path, w, h, fps, pulse_order, cooldown_time, turn_on_time)
    control_dict[position]['turn_on_time'] = turn_on_time
    control_dict[position]['cooldown_time'] = cooldown_time
    
    # intensity vs timeのグラフを生成
    fig_path = os.path.join(project_dir_path, position, 'intensity_vs_time.png')
    mk_fig(fig_path, classified_mmp_dir, w, h, turn_on_time, fps)


write_json(json_path, control_dict)