# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 11:02:19 2017

@author: yiyuezhuo
"""

from utils import unsigned_int,unsigned_char,bin32,bin8
from struct import unpack,pack
from common import decode,decompress
from math import ceil,floor

_keys = [ 0xf0a1, 0xfca1, 0xfda1, 0xfda1, 0xfba1, 0x49a8, 0x4ca8, 0x49a8, 0xfaa1, 0x4aa8, 0x4ba8, 0x4aa8, 0xfba1, 0x49a8, 0x4ca8, 0x49a8 ]
keys = [pack('I',key).decode('gbk')[0] for key in _keys]


def th10decodedata(file, buffer, flength):
    length = unsigned_int(buffer, 0x1c)
    dlength = unsigned_int(buffer, 0x20)
    decodedata = bytearray(dlength)
    rawdata = bytearray(buffer[0x24:])
    
    decode(rawdata, length, 0x400, 0xaa, 0xe1)
    decode(rawdata, length, 0x80, 0x3d, 0x7a)
    #rlength = decompress(rawdata, decodedata, length)
    decompress(rawdata, decodedata, length)

    return decodedata
    
def th10cut(decodedata, verbose = True):
    info = {'meta': decodedata[:0x64], 'stages': {}, 'stage':None,
            'character': None, 'ctype': None, 'rank': None, 'clear': None,
            'code': 0x72303174}
    
    stage = decodedata[0x4c]
    character = unsigned_char(decodedata, 0x50)
    ctype = unsigned_char(decodedata, 0x54)
    rank = unsigned_char(decodedata, 0x58)
    clear = unsigned_char(decodedata, 0x5c)

    info['stage'] = stage
    info['character'] = character
    info['ctype'] = ctype
    info['rank'] = rank
    info['clear'] = clear
    
    stagedata = 0x64

    score = list(range(6))
    faith = list(range(6))
    faith[0] = 5000
    
    for i in range(1, stage):
        stagedata += 0x1c4 + unsigned_int(decodedata, stagedata + 0x8)
        score[i - 1] = unsigned_int(decodedata, stagedata + 0xc)
        faith[i] = unsigned_int(decodedata, stagedata + 0x14)
    score[stage - 1] = unsigned_int(decodedata, 0x10)
    
    
    stagedata = 0x64

    
    for l in range(stage):
        stage_info = {'score': None,'frame': None,'llength': None, 'faith':None,
                      'bin':{'header':None,'replay':None,'tail':None},
                      'index':{'header':None,'replay':None,'tail':None}}
        
        replaydata = stagedata + 0x1c4
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
        stage_info['faith'] = faith[l]
        stage_info['frame'] = frame
        stage_info['llength'] = llength
        stage_info['bin']['header'] = decodedata[stagedata : replaydata]
        stage_info['bin']['replay'] = decodedata[replaydata : (replaydata+(frame*6))]
        stage_info['bin']['tail'] = decodedata[(replaydata+(frame*6)) : (replaydata+llength)]
        stage_info['index']['header'] = (stagedata,replaydata)
        stage_info['index']['replay'] = (replaydata,(replaydata+(frame*6)))
        stage_info['index']['tail'] = ((replaydata+(frame*6)),(replaydata+llength))
        
        info['stages'][l] = stage_info
                
        stagedata += llength + 0x1c4
    
    return info
    
def th10type(character, ctype, rank, clear):
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
        raise Exception("Unrecognized rank {}".format(rank))
    if clear == 8:
        clear_s = 'all'
    elif clear == 7:
        clear_s = 'extra'
    else:
        clear_s = str(clear)
    return character_s, ctype_s, rank_s, clear_s
    
def th10output(info, verbose = True):
    #info = th10cut(decodedata, verbose = verbose)
    stage = info['stage']
    #score = info['score']
    #faith = info['faith']
    score = list(range(stage))
    faith = list(range(stage))
    
    output = []
    #raw_output = []
    
    character, ctype, rank, clear = th10type(info['character'], info['ctype'], info['rank'], info['clear'])
    output.append([' '.join([character, ctype, rank, clear])])
    
    #stagedata = 0x64
    for l in range(stage):
        stage_info = info['stages'][l]
        
        score[l] = stage_info['score']
        faith[l] = stage_info['faith']
        
        replaydata = stage_info['bin']['replay']
        frame = stage_info['frame']
        #llength = stage_info['llength']
        #if verbose:
        #    print('score = {} | frame size = {} | stage length = {} '.format(score[l], frame, llength))
        #    print('void frame = {} frame ratio = {} void frame2 = {}'.format(llength - frame*6, llength / frame, llength - frame*3))
        skey = []
        #raw_output = []
        for i in range(frame):
            if(i % 60 == 0):
                skey.append('[{0:<6}]'.format(i // 60))
            framekey = unsigned_int(replaydata, i * 6) >> 4 & 0xf
            #raw_output.append(unsigned_int(decodedata, replaydata + i * 6))
            #framekey = framekey & 0xf
            skey.append(keys[framekey])
            if((i+1) % 60 == 0):
                output.append(''.join(skey))
                skey = []
        output.append(skey)
    return output
    
def th10decode(file, buffer, flength):
    decodedata = th10decodedata(file, buffer, flength)
    info = th10cut(decodedata)
    output = th10output(info)
    with open('example.txt', 'w') as f:
        f.write('\n'.join([''.join(row) for row in output]))
    with open('example2.txt', 'wb') as f:
        f.write(decodedata)
        
# debug code
        
def _th10cut(file):
    # debug helper
    from common import entry
    file, buffer, flength = entry(file)
    decodedata = th10decodedata(file, buffer, flength)
    return th10cut(decodedata)
    
def _th10decode(file):
    # debug helper
    from common import entry
    file, buffer, flength = entry(file)
    th10decode(file, buffer, flength)
    
def _show(cut_dict, limit = 30):
    # debug helper
    rd = {}
    for key,value in cut_dict.items():
        if isinstance(value,dict):
            rd[key] = _show(value, limit = limit)
        elif len(str(value)) < limit:
            rd[key] = value
        else:
            rd[key] = '...'
    return rd
    
def test(file):
    from common import entry
    file, buffer, flength = entry(file)
    
    length = unsigned_int(buffer, 0x1c)
    dlength = unsigned_int(buffer, 0x20)
    decodedata = bytearray(dlength)
    rawdata = bytearray(buffer[0x24:])
    
    
    def assert_file_eq(obj, path):
        from utils import find_last_match
        with open(path,'rb') as f:
            cont = f.read()
        cut = min(len(obj),len(cont))
        assert obj[:cut] == cont[:cut]
    
    #assert_file_eq(rawdata, '{}.raw.rawdata1'.format(file))
    
    decode(rawdata, length, 0x400, 0xaa, 0xe1)
    
    #assert_file_eq(rawdata, '{}.raw.rawdata2'.format(file))
    
    decode(rawdata, length, 0x80, 0x3d, 0x7a)
    
    #assert_file_eq(rawdata, '{}.raw.rawdata3'.format(file))
    
    decompress(rawdata, decodedata, length)
    
    assert_file_eq(decodedata, '{}.raw'.format(file))
    
    try:
        assert_file_eq(decodedata, '{}.raw'.format(file))
    except AssertionError:
        rawdata = bytearray(buffer[0x24:])
        
        assert_file_eq(rawdata, '{}.raw.rawdata1'.format(file))
        decode(rawdata, length, 0x400, 0xaa, 0xe1)
        assert_file_eq(rawdata, '{}.raw.rawdata2'.format(file))
        decode(rawdata, length, 0x80, 0x3d, 0x7a)
        assert_file_eq(rawdata, '{}.raw.rawdata3'.format(file))

    
    print('test pass')


if __name__ == '__main__':
    
    from utils import diff2,replay_to_binary_seq
    def diff(a,b,raw = False):
        l = diff2(list(a),list(b))
        if not raw:
            print(' '.join([str(c) for c in l]))
            return
        return l
    def d(a,b,raw=False,xor = True):
        if xor:
            l = [sum([int(c) for c in bin(int(i) ^ int(j))[2:]]) for i,j in zip(a,b)]
        else:
            l = [int(i)-int(j) for i,j in zip(a,b)]
            
        if raw:
            return l
        print(l)
    
    th10_01 = _th10cut('replay/th10_01.rpy')
    th10_02 = _th10cut('replay/th10_02.rpy')
    th10_03 = _th10cut('replay/th10_03.rpy')
    th10_null = _th10cut('replay/th10_null.rpy')
    th10_z = _th10cut('replay/th10_z.rpy')
    th10_ex = _th10cut('replay/th10_ex.rpy') # X
    th10_ex2 = _th10cut('replay/th10_ex2.rpy') # shift
    th10_ex3 = _th10cut('replay/th10_ex3.rpy') # ctrl
    
    l10 = replay_to_binary_seq(th10_01['stages'][0]['bin']['replay'])
    l11 = replay_to_binary_seq(th10_01['stages'][1]['bin']['replay'])
    l20 = replay_to_binary_seq(th10_02['stages'][0]['bin']['replay'])
    l21 = replay_to_binary_seq(th10_02['stages'][1]['bin']['replay'])
    ln = replay_to_binary_seq(th10_null['stages'][0]['bin']['replay'])
    lz = replay_to_binary_seq(th10_z['stages'][0]['bin']['replay'])
    lx = replay_to_binary_seq(th10_ex['stages'][0]['bin']['replay'])
    ls = replay_to_binary_seq(th10_ex2['stages'][0]['bin']['replay'])
    lc = replay_to_binary_seq(th10_ex3['stages'][0]['bin']['replay'])
    '''
    th10_04 = _th10cut('replay/th10_04.rpy')
    th10_05 = _th10cut('replay/th10_05.rpy')
    th10_06 = _th10cut('replay/th10_06.rpy')
    th10_ud1990 = _th10cut('replay/th10_ud1990.rpy')
    th10_ud0e78 = _th10cut('replay/th10_ud0e78.rpy')
    h10 = th10_01['stages'][0]['bin']['header']
    h20 = th10_02['stages'][0]['bin']['header']
    h30 = th10_03['stages'][0]['bin']['header']
    h40 = th10_04['stages'][0]['bin']['header']
    h50 = th10_05['stages'][0]['bin']['header']
    h60 = th10_06['stages'][0]['bin']['header']
    h11 = th10_01['stages'][1]['bin']['header']
    h21 = th10_02['stages'][1]['bin']['header']
    h31 = th10_03['stages'][1]['bin']['header']
    h41 = th10_04['stages'][1]['bin']['header']
    h51 = th10_05['stages'][1]['bin']['header']
    h61 = th10_06['stages'][1]['bin']['header']
    t10 = th10_01['stages'][0]['bin']['tail']
    t20 = th10_02['stages'][0]['bin']['tail']
    t30 = th10_03['stages'][0]['bin']['tail']
    t11 = th10_01['stages'][1]['bin']['tail']
    t21 = th10_02['stages'][1]['bin']['tail']
    t31 = th10_03['stages'][1]['bin']['tail']
    hud19900 = th10_ud1990['stages'][0]['bin']['header']
    hud19901 = th10_ud1990['stages'][1]['bin']['header']
    hud0e780 = th10_ud0e78['stages'][0]['bin']['header']
    hud0e781 = th10_ud0e78['stages'][1]['bin']['header']
    tud19900 = th10_ud1990['stages'][0]['bin']['tail']
    tud19901 = th10_ud1990['stages'][1]['bin']['tail']
    tud0e780 = th10_ud0e78['stages'][0]['bin']['tail']
    tud0e781 = th10_ud0e78['stages'][1]['bin']['tail']
    '''