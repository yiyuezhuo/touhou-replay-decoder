# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 11:01:46 2017

@author: yiyuezhuo
"""

#from struct import unpack,pack
from utils import signed_int
from th10 import th10decode
from th11 import th11decode
from common import entry

def run(file):
    file, buffer, flength = entry(file)
    tag = signed_int(buffer, 0)
    if tag == 0x72303174: # th10
        th10decode(file, buffer, flength)
    elif tag == 0x72313174: # th11:
        th11decode(file, buffer, flength)
    else:
        print("Not support format")
        
def test(file):
    # To use the test, you should run the `threp` before(https://github.com/Fluorohydride/threp).

    raw_file = file+'.raw'
    run(file)
    with open('example2.txt','rb') as f:
        content1 = f.read()
    with open(raw_file, 'rb') as f:
        content2 = f.read()
    assert content1 == content2
    print('decode test ok')
    print('parse test comming soon')

def main(argc, argv):
    if argc == 1:
        print("Usage : python {} [filename]".format(argv[0]));
    elif argc == 2:
        run(argv[1])
        
if __name__ == '__main__':
    # simple CLI interface
    import sys
    main(len(sys.argv), sys.argv)