import pandas as pd
import os
import sys
from tqdm import tqdm
from glob import glob
from matplotlib import pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error as calc_mae
import cv2
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json


def video_roi(video_path, frame_order, x, y, w, h):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_order)
    ret, frame = cap.read()
    if ret:
        frame = frame[:,:,0] # gray scaleに変換
        roi = cv2.getRectSubPix(frame, (w, h), (x, y))
        return roi

def img_roi(img_path, x, y, w, h):
    frame = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    roi = cv2.getRectSubPix(frame, (w, h), (x, y))
    return roi

def main(json_path):
    control_dict = read_json(json_path)
    project_dir_path = control_dict['project_dir_path']
    
    df = pd.read_csv(os.path.join(project_dir_path, 'side', 'velocity', 'velocity_{}.csv'.format(control_dict['side']['frame_interval'])))
    data_bool_df = df.loc[(df['data_bool']==True)]
    
    data_num = len(data_bool_df)
    label_memmap = np.memmap(os.path.join(project_dir_path, 'data', 'label.npy'), dtype=np.float16, mode='w+', shape=(data_num, 3))
    input_memmap = np.memmap(os.path.join(project_dir_path, 'data', 'input.npy'), dtype=np.uint8, mode='w+', shape=(data_num, 32, 32, 4))
    
    i = 0
    for idx, row in data_bool_df.iterrows():
        # ラベルを保存
        label = np.array([row['dx'], row['dy'], row['dz']]).astype(np.float16)
        label_memmap[i] = label
        
        # 画像，動画の保存
        w = 32
        h = 32
        img_0 = video_roi(control_dict['side']['mapped_video_path'], frame_order=row['first_frame'], x=row['x'], y=row['y'], w=w, h=h)
        img_1 = video_roi(control_dict['side']['mapped_video_path'], frame_order=row['second_frame'], x=row['x'], y=row['y'], w=w, h=h)
        avg = img_roi(img_path=os.path.join(project_dir_path, 'side', 'mapped_avg.bmp'), x=row['x'], y=row['y'], w=w, h=h)
        background = img_roi(img_path=os.path.join(project_dir_path, 'side', 'mapped_background.bmp'), x=row['x'], y=row['y'], w=w, h=h)
        data = np.array([img_0, img_1, avg, background])
        data = data.transpose(1,2,0)
        input_memmap[i] = data
        
        i += 1

if __name__ == '__main__':
    json_path = input('input json path >')
    main(json_path)