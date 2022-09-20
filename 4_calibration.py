import cv2
import shutil
import os
import numpy as np
import sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json
from experiment.caliblation.calibrator import txt2csv, calibrator, video_processing
from experiment.pre_process.laser_hight import binary_processing, extract_largest_part, calc_laser_height

json_path = input('input json path >')
control_dict = read_json(json_path)
project_dir_path = control_dict['project_dir_path']

for position in ['side', 'bottom']:
    recalib_bool = control_dict['recalib_bool']
    if recalib_bool == True:
        txt_path = os.path.join(project_dir_path, position, 'calibration', 'Cam01', 'Calib01', 'Calibration.cal')
        start_str = 'Error distribution in physical coordinate'
        end_str = 'RMS'
        grid_path = os.path.join(project_dir_path, position, 'grid.csv')
        txt2csv(txt_path, start_str, end_str, save_path=grid_path)
    calib = calibrator(grid_len_phys=5, grid_len_pix=44, csv_path=grid_path) # grid_len_pix は偶数でないとダメ
    if recalib_bool == True:
        calib.pre_processing()
    # 画像の写像
    img_path_list = [os.path.join(project_dir_path, position, 'off.bmp'),
                     os.path.join(project_dir_path, position, 'on.bmp'),
                     os.path.join(project_dir_path, position, 'avg.bmp'),
                     os.path.join(project_dir_path, position, 'background.bmp')]
    for img_path in img_path_list:
        img = cv2.imread(img_path)
        img = calib.transpose(img)
        img_save_path = os.path.join(project_dir_path, position, 'mapped_{}'.format(os.path.basename(img_path)))
        cv2.imwrite(img_save_path, img)
    # 動画の写像
    original_video_path = control_dict[position]['video_path']
    calibed_video_path = os.path.join(project_dir_path, position, 'mapped_{}'.format(os.path.basename(original_video_path)))
    output_size = (img.shape[1], img.shape[0])
    video_processing(original_video_path, calibed_video_path, calib.transpose, output_size)()
    
    # 校正後の動画プロパティを取得する
    cap = cv2.VideoCapture(calibed_video_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    codec = int(cap.get(cv2.CAP_PROP_FOURCC)).to_bytes(4, 'little').decode('utf-8')
    cap.release()
    control_dict[position]['mapped_w'] = w
    control_dict[position]['mapped_h'] = h
    control_dict[position]['mapped_fps'] = fps
    control_dict[position]['mapped_frame'] = frame_num
    control_dict[position]['mapped_codec'] = codec
    
    # レーザーの高さを算出する
    print('レーザーの高さを算出中...')
    img_mapped_on = cv2.imread(os.path.join(project_dir_path, position, 'mapped_on.bmp'), cv2.IMREAD_GRAYSCALE)
    threshold = 250
    img_bin = binary_processing(img_mapped_on, threshold)
    cv2.imwrite(os.path.join(project_dir_path, position, 'on_bin.bmp'), img_bin)
    img_bin = extract_largest_part(img_bin)
    cv2.imwrite(os.path.join(project_dir_path, position, 'on_bin_largest.bmp'), img_bin)
    fig_path = os.path.join(project_dir_path, position, 'laser_height.png')
    a, b = calc_laser_height(img_bin, fig_bool=True, fig_path=fig_path, back_img=img_mapped_on)
    control_dict[position]['a'] = a
    control_dict[position]['b'] = b

write_json(json_path, control_dict)