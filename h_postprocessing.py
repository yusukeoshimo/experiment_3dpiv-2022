import pandas as pd
import os
import sys
from tqdm import tqdm
from matplotlib import pyplot as plt
import numpy as np
from sklearn.metrics import mean_absolute_error as calc_mae
import cv2
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json

def mk_fig(df, save_path):
    x = df.loc[df['data_bool']==True]['dx'].values
    y = df.loc[df['data_bool']==True]['bottom_dx'].values
    
    a, b = np.polyfit(x,y,1)
    mae = calc_mae(x, y)
    data_num = x.shape[0]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot([x.min(), x.max()], [a*x.min()+b, a*x.max()+b], color='red')
    plt.scatter(x, y, s=0.5)
    plt.title('ux vs ux (a:{}, b:{}, mae:{}, n:{})'.format(round(a, 2), round(b, 2), round(mae, 2), data_num))
    plt.xlabel('ux (side camera)')
    plt.ylabel('ux (bottom camera)')
    ax.set_aspect('equal')
    fig.savefig(save_path)
    del fig

def Velocity_vs_FrameOreder(csv_path, save_path):
    df = pd.read_csv(csv_path)
    dx_abs_max = []
    dy_abs_max = []
    dz_abs_max = []
    file_order_list = list(range(df['file_order'].max()))
    for file_order in file_order_list:
        data_df = df.loc[(df['data_bool']==True) & (df['file_order']==file_order)]
        dx_abs_max.append(data_df['dx'].abs().max())
        dy_abs_max.append(data_df['dy'].abs().max())
        dz_abs_max.append(data_df['dz'].abs().max())
    fig = plt.figure()
    plt.plot(file_order_list, dx_abs_max, label='dx')
    plt.plot(file_order_list, dy_abs_max, label='dy')
    plt.plot(file_order_list, dz_abs_max, label='dz')
    plt.legend()
    fig.savefig(save_path)
    del fig

def main(json_path):
    control_dict = read_json(json_path)
    project_dir_path = control_dict['project_dir_path']
    
    for position in ['side', 'bottom']:
        # csvファイルを1つにまとめる
        print('csvファイルを統合中...')
        concat_df = pd.DataFrame(columns=('step_x','step_y','x','y','dx','dy','correlation'))
        for i, csv_name in enumerate(os.listdir(os.path.join(project_dir_path, position, 'velocity', 'flownizer_output'))):
            csv_path = os.path.join(project_dir_path, position, 'velocity', 'flownizer_output', csv_name)
            df = pd.read_csv(csv_path, skiprows=19, usecols=[1,2,3,4,7,8,25], names=('step_x','step_y','x','y','dx','dy','correlation') , encoding='CP932')
            df['step_x'] = df['step_x'] - 1
            df['step_y'] = df['step_y'] - 1
            file_order = int(csv_name.split('.')[0][-4:]) - 1
            df['file_order'] = file_order
            concat_df = pd.concat([concat_df, df])
        concat_df['file_order'] = concat_df['file_order'].astype(int)
        concat_df['step_x'] = concat_df['step_x'].astype(int)
        concat_df['step_y'] = concat_df['step_y'].astype(int)
        concat_df['first_frame'] = 2*concat_df['file_order']
        concat_df['second_frame'] = 2*concat_df['file_order'] + 1
        
        # 外側に面している計算格子かどうか判定する
        concat_df['inner_point'] = (concat_df['step_x'] > concat_df['step_x'].min()) & (concat_df['step_x'] < concat_df['step_x'].max()) & (concat_df['step_y'] > concat_df['step_y'].min()) & (concat_df['step_y'] < concat_df['step_y'].max())
        
        # 普遍的誤ベクトル検知法
        print('普遍的誤ベクトル検知法の実行中...')
        uod_bool_list = []
        inner_df = concat_df.loc[(concat_df['inner_point'] == True)]
        for idx, row in inner_df.iterrows():
            grid_df = concat_df.loc[(concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']-1) & (concat_df['step_y'] == row['step_y']-1)|
                                    (concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']  ) & (concat_df['step_y'] == row['step_y']-1)|
                                    (concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']+1) & (concat_df['step_y'] == row['step_y']-1)|
                                    (concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']-1) & (concat_df['step_y'] == row['step_y']  )|
                                    (concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']+1) & (concat_df['step_y'] == row['step_y']  )|
                                    (concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']-1) & (concat_df['step_y'] == row['step_y']+1)|
                                    (concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']  ) & (concat_df['step_y'] == row['step_y']+1)|
                                    (concat_df['file_order'] == row['file_order']) & (concat_df['step_x'] == row['step_x']+1) & (concat_df['step_y'] == row['step_y']+1)]
            median_x = grid_df['dx'].median()
            median_y = grid_df['dy'].median()
            subtract_x = abs(row['dx'] - median_x)
            subtract_y = abs(row['dy'] - median_y)
            threshold_x = (abs(grid_df['dx']-median_x).median()+0.1)*2
            threshold_y = (abs(grid_df['dy']-median_y).median()+0.1)*2
            uod_bool_list.append((subtract_x < threshold_x) & (subtract_y < threshold_y))
        concat_df.loc[concat_df['inner_point']==True, 'uod'] = uod_bool_list
        
        concat_df.to_csv(os.path.join(project_dir_path, position, 'velocity', 'velocity.csv'))
    
    # bottomのdx, dy, uodをsideに移動
    side_csv_path = os.path.join(project_dir_path, 'side', 'velocity', 'velocity.csv')
    side_df = pd.read_csv(side_csv_path)
    bottom_csv_path = os.path.join(project_dir_path, 'bottom', 'velocity', 'velocity.csv')
    bottom_df = pd.read_csv(bottom_csv_path)
    side_df['bottom_uod'] = bottom_df['uod']
    side_df['bottom_dx'] = bottom_df['dx']
    side_df['dz'] = bottom_df['dy']
    
    # 入力データに使えるインデックスを抽出
    side_df.loc[(side_df['uod']==True) & (side_df['bottom_uod']==True), 'data_bool'] = True
    
    side_df.to_csv(side_csv_path)
    
    # side, bottom共にuodを満たしたデータのuxを算出
    mk_fig(side_df, os.path.join(project_dir_path, 'side', 'ux_vs_ux_{}.png'.format(control_dict['side']['frame_interval'])))
    
    Velocity_vs_FrameOreder(side_csv_path, os.path.join(project_dir_path, 'side', 'velocity_vs_FrameOrder_{}.png'.format(control_dict['side']['frame_interval'])))


if __name__ == '__main__':
    json_path = input('input json path > ')
    main(json_path)