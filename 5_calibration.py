import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.txt_replacement import extract_txt
from util.my_json import read_json, write_json

json_path = input('input json path > ')
control_dict = read_json(json_path)

for position in ['side', 'bottom']:
    print('\n<<<{}>>>'.format(position))
    a = control_dict[position]['a']
    b = control_dict[position]['b']
    w = control_dict[position]['mapped_w']
    yc = round(a*w/2+b, 1)
    ys = yc - 16
    ye = ys + 48 + 1
    xs = 16
    xe = w
    print('計算領域開始点x:{}'.format(xs))
    print('計算領域終点x:{}'.format(xe))
    print('計算領域開始点y:{}'.format(ys))
    print('計算領域終点y:{}'.format(ye))

write_json(json_path, control_dict)