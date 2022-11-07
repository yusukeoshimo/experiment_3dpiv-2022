import shutil
import os
import sys
import subprocess
import pyautogui as pag
import time
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.txt_replacement import extract_txt
from util.my_json import read_json

def click_BottomRight(img_path):
    cx, cy = pag.locateCenterOnScreen(img_path, confidence=0.7)
    rx = cx + int(cv2.imread(img_path).shape[1]/2)
    by = cy + int(cv2.imread(img_path).shape[0]/2)
    pag.click(rx, by)

def click_Right(img_path):
    cx, cy = pag.locateCenterOnScreen(img_path, confidence=0.7)
    rx = cx + int(cv2.imread(img_path).shape[1]/2)
    pag.click(rx, cy)

def main(json_path, inner_len, outer_len, interval):
    control_dict = read_json(json_path)
    project_dir_path = control_dict['project_dir_path']
    for position in ['side', 'bottom']:
        # 校正画像の読込
        calib_img_src = os.path.join(project_dir_path, position, 'mapped_off.bmp')
        calib_img_dst = os.path.join(project_dir_path, position, 'piv', 'Cam01', 'Calib01', 'CalibImage.png')
        shutil.copy2(calib_img_src, calib_img_dst)
        
        # 簡易キャリブレーションの設定をする
        src_CalibraionParameters = r'F:\3DPIV-2022\project\0_src_alias\auto_piv\CalibrationParameters.xml'
        dst_CalibraionParameters = os.path.join(project_dir_path, position, 'piv', 'Cam01', 'Calib01', 'CalibrationParameters.xml')
        shutil.copy2(src_CalibraionParameters, dst_CalibraionParameters)
        
        # gui操作
        cmd = 'call {} {}'.format(r'"c:\Users\student\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Ditect\Flownizer64 Ver.1.2.5.lnk"', os.path.join(project_dir_path, position, 'piv', 'piv.di5'))
        returncode = subprocess.run(cmd, shell=True)
        time.sleep(3)
        button_path_list = [r'F:\3DPIV-2022\project\0_src_alias\auto_piv\img_for_calibration.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\execute_calibration.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\simple_calibration.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\create_calibration_file.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\ok.png']
        for button_path in button_path_list:
            while True:
                try:
                    x, y = pag.locateCenterOnScreen(button_path, confidence=0.95)
                    pag.click(x, y)
                    time.sleep(3)
                    break
                except:
                    pass
        cmd = 'taskkill /f /im flownizer.exe'
        returncode = subprocess.run(cmd, shell=True)
        
        flownizer_output_dir = os.path.join(project_dir_path, position, 'velocity', 'flownizer_output')
        shutil.rmtree(flownizer_output_dir)
        os.mkdir(flownizer_output_dir)
        
        # 粒子画像の読込
        src_InputInfo = r'F:\3DPIV-2022\project\0_src_alias\auto_piv\InputInfo.xml'
        dst_InputInfo = os.path.join(project_dir_path, position, 'piv', 'Cam01', 'Take01', 'InputInfo.xml')
        with open(src_InputInfo) as f:
            txt = f.read()
        src_FrameTotal = extract_txt(txt, '<FrameTotal>', '</FrameTotal>')
        src_ImageDirectory = extract_txt(txt, '<ImageDirectory>', '</ImageDirectory>')
        src_ImageFilename = extract_txt(txt, '<ImageFilename>', '</ImageFilename>')
        src_LastFrame = extract_txt(txt, '<LastFrame>', '</LastFrame>')
        src_SelectionEnd = extract_txt(txt, '<SelectionEnd>', '</SelectionEnd>')
        dst_FrameTotal = str(control_dict[position]['mapped_frame'])
        dst_ImageFilename = os.path.basename(control_dict[position]['mapped_video_path'])
        dst_ImageDirectory = control_dict[position]['mapped_video_path'][:-(len(dst_ImageFilename)+1)]
        dst_LastFrame = str(control_dict[position]['mapped_frame'] - 1)
        dst_SelectionEnd = str(control_dict[position]['mapped_frame'] - 1)
        for i in range(len(src_FrameTotal)):
            txt = txt.replace('<FrameTotal>'+src_FrameTotal[i]+'</FrameTotal>', '<FrameTotal>'+dst_FrameTotal+'</FrameTotal>')
        for i in range(len(src_ImageDirectory)):
            txt = txt.replace('<ImageDirectory>'+src_ImageDirectory[i]+'</ImageDirectory>', '<ImageDirectory>'+dst_ImageDirectory+'</ImageDirectory>')
        for i in range(len(src_ImageFilename)):
            txt = txt.replace('<ImageFilename>'+src_ImageFilename[i]+'</ImageFilename>', '<ImageFilename>'+dst_ImageFilename+'</ImageFilename>')
        for i in range(len(src_LastFrame)):
            txt = txt.replace('<LastFrame>'+src_LastFrame[i]+'</LastFrame>', '<LastFrame>'+dst_LastFrame+'</LastFrame>')
        for i in range(len(src_SelectionEnd)):
            txt = txt.replace('<SelectionEnd>'+src_SelectionEnd[i]+'</SelectionEnd>', '<SelectionEnd>'+dst_SelectionEnd+'</SelectionEnd>')
        with open(dst_InputInfo, mode='w') as f:
            f.write(txt)
        
        # 比較フレームの設定
        src_FrameCalibrationParameters = r'F:\3DPIV-2022\project\0_src_alias\auto_piv\FrameCalibrationParameters.xml'
        dst_FrameCalibrationParameters = os.path.join(project_dir_path, position, 'piv', 'Cam01', 'Take01', 'FrameCalibrationParameters.xml')
        shutil.copy2(src_FrameCalibrationParameters, dst_FrameCalibrationParameters)
        
        # 計算領域の設定
        src_InterrogationParameters = r'F:\3DPIV-2022\project\0_src_alias\auto_piv\InterrogationParameters.xml'
        dst_InterrogationParameters = os.path.join(project_dir_path, position, 'piv', 'Cam01', 'Take01', 'InterrogationParameters.xml')
        with open(src_InterrogationParameters) as f:
            txt = f.read()
        src_Mdx = extract_txt(txt, '<Mdx>', '</Mdx>')
        src_Mdy = extract_txt(txt, '<Mdy>', '</Mdy>')
        src_Mx0 = extract_txt(txt, '<Mx0>', '</Mx0>')
        src_Mx1 = extract_txt(txt, '<Mx1>', '</Mx1>')
        src_My0 = extract_txt(txt, '<My0>', '</My0>')
        src_My1 = extract_txt(txt, '<My1>', '</My1>')
        a = control_dict[position]['a']
        b = control_dict[position]['b']
        w = control_dict[position]['mapped_w']
        dst_Mdx = str(interval)
        dst_Mdy = str(interval)
        dst_Mx0 = str(outer_len/2)
        dst_Mx1 = str(w-outer_len/2)
        dst_My0 = str(round(a*w/2+b, 1) - interval)
        dst_My1 = str(round(a*w/2+b, 1) + 2*interval)
        for i in range(len(src_Mdx)):
            txt = txt.replace('<Mdx>'+src_Mdx[i]+'</Mdx>', '<Mdx>'+dst_Mdx+'</Mdx>')
        for i in range(len(src_Mdy)):
            txt = txt.replace('<Mdy>'+src_Mdy[i]+'</Mdy>', '<Mdy>'+dst_Mdy+'</Mdy>')
        for i in range(len(src_Mx0)):
            txt = txt.replace('<Mx0>'+src_Mx0[i]+'</Mx0>', '<Mx0>'+dst_Mx0+'</Mx0>')
        for i in range(len(src_Mx1)):
            txt = txt.replace('<Mx1>'+src_Mx1[i]+'</Mx1>', '<Mx1>'+dst_Mx1+'</Mx1>')
        for i in range(len(src_My0)):
            txt = txt.replace('<My0>'+src_My0[i]+'</My0>', '<My0>'+dst_My0+'</My0>')
        for i in range(len(src_My1)):
            txt = txt.replace('<My1>'+src_My1[i]+'</My1>', '<My1>'+dst_My1+'</My1>')
        # 検査領域の設定
        src_Ofx = extract_txt(txt, '<Ofx>', '</Ofx>')
        src_Ofy = extract_txt(txt, '<Ofy>', '</Ofy>')
        src_Rx = extract_txt(txt, '<Rx>', '</Rx>')
        src_Ry = extract_txt(txt, '<Ry>', '</Ry>')
        src_Tx = extract_txt(txt, '<Tx>', '</Tx>')
        src_Ty = extract_txt(txt, '<Ty>', '</Ty>')
        dst_Ofx = str(int(-(outer_len-inner_len)/2))
        dst_Ofy = str(int(-(outer_len-inner_len)/2))
        dst_Rx = str(inner_len)
        dst_Ry = str(inner_len)
        dst_Tx = str(outer_len)
        dst_Ty = str(outer_len)
        for i in range(len(src_Ofx)):
            txt = txt.replace('<Ofx>'+src_Ofx[i]+'</Ofx>', '<Ofx>'+dst_Ofx+'</Ofx>')
        for i in range(len(src_Ofy)):
            txt = txt.replace('<Ofy>'+src_Ofy[i]+'</Ofy>', '<Ofy>'+dst_Ofy+'</Ofy>')
        for i in range(len(src_Rx)):
            txt = txt.replace('<Rx>'+src_Rx[i]+'</Rx>', '<Rx>'+dst_Rx+'</Rx>')
        for i in range(len(src_Ry)):
            txt = txt.replace('<Ry>'+src_Ry[i]+'</Ry>', '<Ry>'+dst_Ry+'</Ry>')
        for i in range(len(src_Tx)):
            txt = txt.replace('<Tx>'+src_Tx[i]+'</Tx>', '<Tx>'+dst_Tx+'</Tx>')
        for i in range(len(src_Ty)):
            txt = txt.replace('<Ty>'+src_Ty[i]+'</Ty>', '<Ty>'+dst_Ty+'</Ty>')
        # 計算詳細設定
        src_Tolerance = extract_txt(txt, '<Tolerance>', '</Tolerance>')
        src_Cbc = extract_txt(txt, '<Cbc>', '</Cbc>')
        src_IgnoreCorrave = extract_txt(txt, '<IgnoreCorrave>', '</IgnoreCorrave>')
        dst_Tolerance = '9999'
        dst_Cbc = '0'
        dst_IgnoreCorrave = 'true'
        for i in range(len(src_Tolerance)):
            txt = txt.replace('<Tolerance>'+src_Tolerance[i]+'</Tolerance>', '<Tolerance>'+dst_Tolerance+'</Tolerance>')
        for i in range(len(src_Cbc)):
            txt = txt.replace('<Cbc>'+src_Cbc[i]+'</Cbc>', '<Cbc>'+dst_Cbc+'</Cbc>')
        for i in range(len(src_IgnoreCorrave)):
            txt = txt.replace('<IgnoreCorrave>'+src_IgnoreCorrave[i]+'</IgnoreCorrave>', '<IgnoreCorrave>'+dst_IgnoreCorrave+'</IgnoreCorrave>')
        with open(dst_InterrogationParameters, mode='w') as f:
            f.write(txt)
        
        # gui操作
        cmd = 'call {} {}'.format(r'"c:\Users\student\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Ditect\Flownizer64 Ver.1.2.5.lnk"', os.path.join(project_dir_path, position, 'piv', 'piv.di5'))
        returncode = subprocess.run(cmd, shell=True)
        time.sleep(3)
        button_path_list = [r'F:\3DPIV-2022\project\0_src_alias\auto_piv\calculation.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\execute_2d2cpiv.png']
        for button_path in button_path_list:
            while True:
                try:
                    x, y = pag.locateCenterOnScreen(button_path, confidence=0.95)
                    pag.click(x, y)
                    time.sleep(3)
                    break
                except:
                    pass
        button_path_list = [r'F:\3DPIV-2022\project\0_src_alias\auto_piv\start_measurement.png']
        for button_path in button_path_list:
            while True:
                try:
                    x, y = pag.locateCenterOnScreen(button_path, confidence=0.95)
                    pag.click(x, y)
                    time.sleep(30)
                    break
                except:
                    pass
        button_path_list = [r'F:\3DPIV-2022\project\0_src_alias\auto_piv\ok_2d2cpiv_finished.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\vector.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\display_vector.png']
        for button_path in button_path_list:
            while True:
                try:
                    x, y = pag.locateCenterOnScreen(button_path, confidence=0.95)
                    pag.click(x, y)
                    time.sleep(3)
                    break
                except:
                    pass
        button_path_list = [r'F:\3DPIV-2022\project\0_src_alias\auto_piv\triangle_of_vector.png']
        for button_path in button_path_list:
            while True:
                try:
                    click_BottomRight(button_path)
                    time.sleep(3)
                    break
                except:
                    pass
        button_path_list = [r'F:\3DPIV-2022\project\0_src_alias\auto_piv\save_csv.png',
                            r'F:\3DPIV-2022\project\0_src_alias\auto_piv\save.png']
        for button_path in button_path_list:
            while True:
                try:
                    x, y = pag.locateCenterOnScreen(button_path, confidence=0.95)
                    pag.click(x, y)
                    time.sleep(3)
                    break
                except:
                    pass
        
        pag.hotkey('ctrl', 'l')
        pag.typewrite('{}'.format(os.path.join(project_dir_path, position, 'velocity', 'flownizer_output')))
        pag.hotkey('enter')
        
        time.sleep(10)
        button_path_list = [r'F:\3DPIV-2022\project\0_src_alias\auto_piv\file_name.png']
        for button_path in button_path_list:
            while True:
                try:
                    click_Right(button_path)
                    time.sleep(3)
                    break
                except:
                    pass
        pag.typewrite('{}_'.format(control_dict[position]['frame_interval']))
        pag.hotkey('enter')
        time.sleep(30)
        cmd = 'taskkill /f /im flownizer.exe'
        returncode = subprocess.run(cmd, shell=True)

if __name__ == '__main__':
    json_path = input('input json path >')
    inner_len = int(input('検査領域の一辺の長さを入力> '))
    outer_len = int(input('探査領域の一辺の長さを入力> '))
    interval = int(input('計測点間距離を入力> '))
    main(json_path, inner_len, outer_len, interval)