# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 13:28:44 2017

@author: yiyuezhuo
"""

import threp
from api import look,cut_scan
from utils import replay_to_binary_seq

threp.test('test_case/th10_02.rpy')

threp.run('test_case/th10_05.rpy')

cut_scan('test_case/origin','test_case/target')

output = look('test_case/target/th10_01.rpy.pickle')
print('\n'.join([''.join(line) for line in output[-100:]]))

import pickle

your_pickle_path = 'test_case/target/th10_01.rpy.pickle'
with open(your_pickle_path, 'rb') as f:
    info = pickle.load(f)
stage = info['stages'][0]
replay = stage['bin']['replay']
print(replay[:100])
seq = replay_to_binary_seq(replay)
print(seq[10:20])

print('test end')
