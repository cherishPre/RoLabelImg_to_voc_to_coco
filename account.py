# -*- coding: utf-8
import os
import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def get_dir_info(dir_path, deep=0, info=None):
    if info is None:
        info = {'deep': 0, 'deep_dir': '', 'file_num': 0, 'dir_num': 0}
    if deep > info['deep']:
        info['deep'] = deep
        info['deep_dir'] = dir_path
    file_list = os.listdir(dir_path)
    for file in file_list:
        file_path = os.path.join(dir_path, file)
        if os.path.isdir(file_path):
            info['dir_num'] += 1
            get_dir_info(file_path, deep=deep+1, info=info)
        else:
            if '.xml' in file:
                info['file_num'] += 1
    if deep == 0:
        return info

if __name__ == '__main__':
    dir_path = "./"
    s = time.time()
    d = get_dir_info(dir_path)
    print("{}".format(time.time() - s))
    print(d)
