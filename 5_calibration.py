import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from util.txt_replacement import extract_txt
from util.my_json import read_json, write_json

json_path = input('input json path > ')
control_dict = read_json(json_path)
inner_len = int(input('検査領域の一辺の長さを入力> '))
outer_len = int(input('探査領域の一辺の長さを入力> '))
interval = int(input('input interval > '))

for position in ['side', 'bottom']:
    print('\n<<<{}>>>'.format(position))
    a = control_dict[position]['a']
    b = control_dict[position]['b']
    w = control_dict[position]['mapped_w']
    yc = round(a*w/2+b, 1)
    ys = yc - interval
    ye = yc + 2*interval
    xs = outer_len/2
    xe = w-outer_len/2
    print('計算領域開始点x:{}'.format(xs))
    print('計算領域終点x:{}'.format(xe))
    print('計算領域開始点y:{}'.format(ys))
    print('計算領域終点y:{}'.format(ye))

write_json(json_path, control_dict)