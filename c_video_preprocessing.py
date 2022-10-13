import cv2
import shutil
import os
import numpy as np
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json
from experiment.pre_process.backgroung_processing import extract_background, subtract
from experiment.pre_process.intensity_avg import avg_memmaps
from experiment.pre_process.laser_hight import binary_processing, extract_largest_part
from experiment.classification.mk_video4flownizer import main as mk_video4flownizer

def main(json_path, frame_interval):
    control_dict = read_json(json_path)
    project_dir_path = control_dict['project_dir_path']

    for position in ['side', 'bottom']:
        print('\n\n<<<{}ディレクトリの処理開始>>>\n'.format(position))
        
        # 背景処理
        print('背景処理中...')
        memmap_dir = os.path.join(project_dir_path, position, 'memmap')
        w = control_dict[position]['raw_video_w']
        h = control_dict[position]['raw_video_h']
        left_cut = 3
        right_cut = 3
        background_img = extract_background(memmap_dir, w, h, left_cut, right_cut)
        cv2.imwrite(os.path.join(project_dir_path, position, 'background.bmp'), background_img)
        subtract_dir = os.path.join(project_dir_path, position, 'subtract')
        subtract(subtract_dir, memmap_dir, background_img)
        
        # 平均輝度処理
        print('平均輝度を算出中...')
        intensity_avg_img = avg_memmaps(subtract_dir, w, h, left_cut, right_cut)
        cv2.imwrite(os.path.join(project_dir_path, position, 'avg.bmp'), intensity_avg_img)
        
        # 平均輝度を二値化
        print('平均輝度を二値化...')
        threshold = np.amax(intensity_avg_img*0.6)
        binary_img = binary_processing(intensity_avg_img, threshold)
        binary_img = binary_img.astype(np.uint8)
        binary_img = extract_largest_part(binary_img)
        cv2.imwrite(os.path.join(project_dir_path, position, 'avg_bin.bmp'), binary_img)
        
        # 動画を作成
        print('動画を作成中...')
        pulse_order = control_dict[position]['pulse_order']
        if pulse_order == 'first':
            cut_edge = right_cut
        elif pulse_order == 'second':
            cut_edge = left_cut
        codec = control_dict[position]['raw_video_codec']
        video_path = os.path.join(project_dir_path, position, 'FrameInterval_{}.avi'.format(frame_interval))
        control_dict[position]['video_path'] = video_path
        mk_video4flownizer(video_path, pulse_order, frame_interval, cut_edge, subtract_dir, h, w, codec)

    write_json(json_path, control_dict)


if __name__ == '__main__':
    json_path = input('input json path > ')
    frame_interval = int(input('input frame_interval >'))
    main(json_path, frame_interval)