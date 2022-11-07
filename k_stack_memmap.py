import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from experiment.LightGBM.func.stack_memmap import stack_memmap
from glob import glob
import numpy as np

project_dir_path = input('input dir saved project dir >')
save_dir = input('input save dir >')

input_path_list = glob(os.path.join(project_dir_path, 'project*', 'data', 'input.npy'))
stack_input_path = os.path.join(save_dir, 'input.npy')
stack_memmap(input_path_list, stack_input_path, 32, 32)

label_path_list = glob(os.path.join(project_dir_path, 'project*', 'data', 'label.npy'))
stack_label_path = os.path.join(save_dir, 'label.npy')
stack_memmap(label_path_list, stack_label_path, 1, 1, dtype=np.float16)