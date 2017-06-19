# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 09:08:27 2017

@author: yiyuezhuo
"""

from utils import unsigned_int,bin32,bin8,unsigned_char
from struct import unpack,pack
from common import decode,decompress
from math import ceil,floor

_keys = [ 0xf0a1, 0xfca1, 0xfda1, 0xfda1, 0xfba1, 0x49a8, 0x4ca8, 0x49a8, 0xfaa1, 0x4aa8, 0x4ba8, 0x4aa8, 0xfba1, 0x49a8, 0x4ca8, 0x49a8 ]
keys = [pack('I',key).decode('gbk')[0] for key in _keys]


def th11decodedata(file, buffer, flength):
    length = unsigned_int(buffer, 0x1c)
    dlength = unsigned_int(buffer, 0x20)
    decodedata = bytearray(dlength)
    rawdata = bytearray(buffer[0x24:])
    
    decode(rawdata, length, 0x800, 0xaa, 0xe1)
    decode(rawdata, length, 0x40, 0x3d, 0x7a)
    decompress(rawdata, decodedata, length)

    return decodedata

def th11cut(decodedata, verbose = True):
    info = {'meta': decodedata[:0x70], 'stages': {}, 'stage':None,
            'character': None, 'ctype': None, 'rank': None, 'clear': None,
            'code': 0x72313174}
    
    stage = decodedata[0x58]
    character = unsigned_char(decodedata, 0x5c)
    ctype = unsigned_char(decodedata, 0x60)
    rank = unsigned_char(decodedata, 0x64)
    clear = unsigned_char(decodedata, 0x68)

    info['stage'] = stage
    info['character'] = character
    info['ctype'] = ctype
    info['rank'] = rank
    info['clear'] = clear

    stagedata = 0x70
    score = list(range(6))
    
    for i in range(1, stage):
        stagedata += 0x90 + unsigned_int(decodedata, stagedata + 0x8)
        score[i - 1] = unsigned_int(decodedata, stagedata + 0xc)
    score[stage - 1] = unsigned_int(decodedata, 0x14)
    
    info['stage'] = stage
    
    stagedata = 0x70
    
    for l in range(stage):
        stage_info = {'score': None,'frame': None,'llength': None,
                      'bin':{'header':None,'replay':None,'tail':None},
                      'index':{'header':None,'replay':None,'tail':None}}
        
        replaydata = stagedata + 0x90
        frame = unsigned_int(decodedata, stagedata + 0x4)
        llength = unsigned_int(decodedata, stagedata + 0x8)
        if frame * 6 + ceil(frame/30) == llength:
            pass
        elif frame* 3 + ceil(frame/60) == llength:
            frame //= 2
        else:
            print('!Unknow frame pattern, try to detect true frame size througn stage length')
            frame = floor(llength / (6+1/30))
        
        if verbose:
            print('score = {} | frame size = {} | stage length = {} '.format(score[l], frame, llength))
            #print('void frame = {} frame ratio = {} void frame2 = {}'.format(llength - frame*6, llength / frame, llength - frame*3))

        stage_info['score'] = score[l]
        stage_info['frame'] = frame
        stage_info['llength'] = llength
        stage_info['bin']['header'] = decodedata[stagedata : replaydata]
        stage_info['bin']['replay'] = decodedata[replaydata : (replaydata+(frame*6))]
        stage_info['bin']['tail'] = decodedata[(replaydata+(frame*6)) : (replaydata+llength)]
        stage_info['index']['header'] = (stagedata,replaydata)
        stage_info['index']['replay'] = (replaydata,(replaydata+(frame*6)))
        stage_info['index']['tail'] = ((replaydata+(frame*6)),(replaydata+llength))
        
        info['stages'][l] = stage_info
                
        stagedata += llength + 0x90
    
    return info
    
def th11type(character, ctype, rank, clear):
    # (unsigned_char*4) -> (string*4)
    if character == 0:
        character_s = 'Reimu'
    elif character == 1:
        character_s = 'Marisa'
    else:
        raise Exception("Unrecognized character {}".format(character))
    if ctype == 0:
        ctype_s = 'A'
    elif ctype == 1:
        ctype_s = 'B'
    elif ctype == 2:
        ctype_s = 'C'
    else:
        raise Exception("Unrecognized ctype {}".format(ctype))
    if rank == 0:
        rank_s = 'easy'
    elif rank == 1:
        rank_s = 'normal'
    elif rank == 2:
        rank_s = 'hard'
    elif rank == 3:
        rank_s = 'lunatic'
    elif rank == 4:
        rank_s = 'extra'
    else:
        # I have not handle extra case
        raise Exception("Unrecognized rank {}".format(rank))
    if clear == 8:
        clear_s = 'all'
    elif clear == 7:
        clear_s = 'extra'
    else:
        clear_s = str(clear)
    return character_s, ctype_s, rank_s, clear_s


def th11output(info, verbose = True):
    #info = th11cut(decodedata, verbose = verbose)
    stage = info['stage']
    score = list(range(stage))
    
    output = []
    
    character, ctype, rank, clear = th11type(info['character'], info['ctype'], info['rank'], info['clear'])
    output.append([' '.join([character, ctype, rank, clear])])
    
    for l in range(stage):
        stage_info = info['stages'][l]
        
        score[l] = stage_info['score']
        
        replaydata = stage_info['bin']['replay']
        frame = stage_info['frame']
        #llength = stage_info['llength']
        #if verbose:
        #    print('score = {} | frame size = {} | stage length = {} '.format(score[l], frame, llength))
        #    print('void frame = {} frame ratio = {} void frame2 = {}'.format(llength - frame*6, llength / frame, llength - frame*3))
        skey = []
        for i in range(frame):
            if(i % 60 == 0):
                skey.append('[{0:<6}]'.format(i // 60))
            framekey = unsigned_int(replaydata, i * 6) >> 4 & 0xf
            skey.append(keys[framekey])
            if((i+1) % 60 == 0):
                output.append(''.join(skey))
                skey = []
        output.append(skey)
    return output

def th11decode(file, buffer, flength):
    decodedata = th11decodedata(file, buffer, flength)
    info = th11cut(decodedata)
    output = th11output(info)
    with open('example.txt', 'w') as f:
        f.write('\n'.join([''.join(row) for row in output]))
    with open('example2.txt', 'wb') as f:
        f.write(decodedata)

if __name__ == '__main__':
    pass