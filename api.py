# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 10:55:14 2017

@author: yiyuezhuo
"""

import th10 as _th10
import th11 as _th11
from common import entry
from utils import signed_int
import os
import pickle


class Th:
    code = None
    _decodedata = None
    _cut = None
    _type = None
    _output = None
    _decode = None
    @classmethod
    def cut(cls, file):
        file, buffer, flength = entry(file)
        decodedata = cls._decodedata(file, buffer, flength)
        return cls._cut(decodedata)


class Th10(Th):
    code = 0x72303174
    _decodedata = _th10.th10decodedata
    _cut = _th10.th10cut
    _type = _th10.th10type
    _output = _th10.th10output
    _decode = _th10.th10decode
    
class Th11(Th):
    code = 0x72313174
    _decodedata = _th11.th11decodedata
    _cut = _th11.th11cut
    _type = _th11.th11type
    _output = _th11.th11output
    _decode = _th11.th11decode
    
check_th = {th.code:th for th in [Th10, Th11]}

def file_command(path, command):
    file, buffer, flength = entry(path)
    tag = signed_int(buffer, 0)
    th = check_th[tag]
    return getattr(th, command)(path)
    
def scan_command(command, origin_dir, target_dir):
    os.makedirs(target_dir,exist_ok=True)
        
    for name in os.listdir(origin_dir):
        if not name.endswith('.rpy'):
            continue
        path = os.path.join(origin_dir, name)
        target_path = os.path.join(target_dir, name+'.pickle')
        info = file_command(path, command)
        with open(target_path, 'wb') as f:
            pickle.dump(info, f)
        print('{} -> {}'.format(path, target_path))

def cut_scan(origin_dir, target_dir):
    # transform all *.rpy files included in origin_dir to python pickled 
    # file into target_dir
    scan_command('cut', origin_dir, target_dir)

def look(pickle_path):
    # look whether the pickle file is normal.
    with open(pickle_path, 'rb') as f:
        info = pickle.load(f)
    return check_th[info['code']]._output(info)