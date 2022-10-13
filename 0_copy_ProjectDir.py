from asyncore import write
import subprocess
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.my_json import read_json, write_json
from util.txt_replacement import extract_txt
from util import winpath
import shutil
import glob

def main():
    copied_path = input('input project dir path you would like to copy >')
    pasted_dir = winpath.join(*copied_path.split('\\')[:-1])
    old_project_name = copied_path.split('\\')[-1]
    new_project_name = 'project_{}_{}_{}_{}_{}_{}'.format(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, datetime.now().minute, datetime.now().second)
    new_project_path = os.path.join(pasted_dir, new_project_name)

    old_json_path = os.path.join(copied_path, 'system', 'control_dict.json')
    new_json_path = os.path.join(new_project_path, 'system', 'control_dict.json')

    # ディレクトリのコピー
    cmd = 'xcopy /t /e "{}" "{}\\"'.format(copied_path, new_project_path)
    returncode = subprocess.call(cmd)

    # jsonファイルのコピー，リセット，新しい書き込み，保存
    old_d = read_json(old_json_path)
    new_d = {key : None for key in old_d.keys()}
    new_d['project_dir_path'] = new_project_path
    for position in ['side', 'bottom']:
        new_d[position] = {}
    write_json(new_json_path, new_d)
    
    # iccaptureのファイルをコピー
    src_iccf = glob.glob(os.path.join(copied_path, 'system', '*.iccf'))[0]
    dst_iccf = os.path.join(new_project_path, 'system', os.path.basename(src_iccf))
    shutil.copy2(src_iccf, dst_iccf)
    
    # LightGBMモデルのコピー，パスをjsonに追加
    new_d = read_json(new_json_path)
    for position in ['side', 'bottom']:
        old_LightGBM_path = os.path.join(copied_path, position, 'LightGBM', 'my_LightGBM.pkl')
        new_LightGBM_path = os.path.join(new_project_path, position, 'LightGBM', 'my_LightGBM.pkl')
        shutil.copy2(old_LightGBM_path, new_LightGBM_path)
        new_d[position]['LightGBM_model_path'] = new_LightGBM_path
    write_json(new_json_path, new_d)

    # LightGBMモデルの学習データをコピー
    old_d = read_json(old_json_path)
    new_d = read_json(new_json_path)
    for position in ['side', 'bottom']:
        # LightGBMモデルの入力データをコピー，パスをjsonに書き込み
        new_d[position]['learning_input_path'] = old_d[position]['learning_input_path'].replace(old_project_name, new_project_name)
        shutil.copy2(old_d[position]['learning_input_path'], new_d[position]['learning_input_path'])
        # LightGBMモデルのラベルデータをコピー，パスをjsonに書き込み
        new_d[position]['learning_label_path'] = old_d[position]['learning_label_path'].replace(old_project_name, new_project_name)
        shutil.copy2(old_d[position]['learning_label_path'], new_d[position]['learning_label_path'])
    write_json(new_json_path, new_d)
    
    # calibration.di5, piv.di5の一部修正＋コピー
    for position in ['side', 'bottom']:
        # calibration.di5
        old_calibration_path = os.path.join(copied_path, position, 'calibration')
        new_calibration_path = os.path.join(new_project_path, position, 'calibration')
        with open(os.path.join(old_calibration_path, 'calibration.di5')) as f:
            txt = f.read()
        file_path = extract_txt(txt, '<ProjectPath>', '</ProjectPath>')[0]
        file_list = file_path.split('\\')
        file_list[-3] = new_project_name
        txt.replace(file_path, winpath.join(*file_list))
        with open(os.path.join(new_calibration_path, 'calibration.di5'), mode='w') as f:
            f.write(txt)
        # piv.di5
        old_piv_path = os.path.join(copied_path, position, 'piv')
        new_piv_path = os.path.join(new_project_path, position, 'piv')
        with open(os.path.join(old_piv_path, 'piv.di5')) as f:
            txt = f.read()
        file_path = extract_txt(txt, '<ProjectPath>', '</ProjectPath>')[0]
        file_list = file_path.split('\\')
        file_list[-3] = new_project_name
        txt.replace(file_path, winpath.join(*file_list))
        with open(os.path.join(new_piv_path, 'piv.di5'), mode='w') as f:
            f.write(txt)
    
    y_or_n = input('recalib? (y or n) >')
    for position in ['side', 'bottom']:
        if y_or_n == 'y':
            recalib_bool = True
        elif y_or_n == 'n':
            recalib_bool = False
            shutil.copy2(os.path.join(copied_path, position, 'grid.csv'), os.path.join(new_project_path, position, 'grid.csv'))
            shutil.copy2(os.path.join(copied_path, position, 'on.bmp'), os.path.join(new_project_path, position, 'on.bmp'))
            shutil.copy2(os.path.join(copied_path, position, 'off.bmp'), os.path.join(new_project_path, position, 'off.bmp  '))
            new_d = read_json(new_json_path)
        new_d['recalib_bool'] = recalib_bool
        write_json(new_json_path, new_d)
    
    # jsonファイルにレーザーの点滅の順番を記入
    new_d = read_json(new_json_path)
    new_d['side']['pulse_order'] = 'first'
    new_d['bottom']['pulse_order'] = 'second'
    write_json(new_json_path, new_d)
    
if __name__ == '__main__':
    main()                      