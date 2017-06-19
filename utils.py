# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 09:05:09 2017

@author: yiyuezhuo
"""

from struct import pack, unpack

def unsigned_int(_bytes, pointer):
    return unpack('I', _bytes[pointer:pointer+4])[0]
def unsigned_char(_bytes, pointer):
    return unpack('B', _bytes[pointer:pointer+1])[0]
def signed_int(_bytes, pointer):
    return unpack('i', _bytes[pointer:pointer+4])[0]

def bin32(num):
    return '{0:>32}'.format(bin(num)[2:]).replace(' ','0')
def bin8(num):
    return '{0:>8}'.format(bin(num)[2:]).replace(' ','0')
def bin16(num):
    return '{0:>16}'.format(bin(num)[2:]).replace(' ','0')



class Ref(object):
    pass

def diff2(s1, s2):
    import difflib
    # It include inplace modify.
    
    #s1 = [w.strip() for w in A.split(' ') if len(w.strip())>0]
    #s2 = [w.strip() for w in B.split(' ') if len(w.strip())>0]
    
    matcher = difflib.SequenceMatcher(None, s1, s2)
    #ratio = matcher.ratio()
    
    rl = []
    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
        #print(tag, i1, i2, j1, j2)
        if tag == 'delete':
            rl = ['[-'] + s1[i1:i2] + ['-]'] + rl
            del s1[i1:i2]
        elif tag == 'equal':
            rl = s1[i1:i2] + rl
        elif tag == 'insert':
            rl =  ['[+'] + s2[j1:j2] + ['+]'] + rl
            s1[i1:i2] = s2[j1:j2]
        elif tag == 'replace':
            rl = ['['] + s1[i1:i2] + ['->'] + s2[j1:j2] + [']'] + rl
            s1[i1:i2] = s2[j1:j2]
    return rl
    
def find_last_true(l, pred):
    assert pred(l[0])
    left = 0
    right = len(l)
    while right - left >= 2:
        #print(left,right)
        check = left + (right - left)//2
        if pred(l[check]):
            left = check
        else:
            right = check
    return right if pred(right) else left

def find_last_match(seq1, seq2):
    pred = lambda cut:seq1[:cut] == seq2[:cut]
    length = min(len(seq1),len(seq2))
    return find_last_true(list(range(length)), pred)

def replay_to_binary_seq(replay):
    '''
    The below content is based on th10
    When frame(6 byte, 48 bit) is unpacked by `IH`
    000000000000000000000000010000000000000000000000
    ********************************                interger 32 binary(I)
                                    ****************short 16 binary(H)
    000000000000000000000000000100000000000000000000
                            ****                    arrow key
                               *                    up(0-index -> 27)
                             *                      left(0-index -> 25)
                              *                     down(0-index -> 26)
                            *                       right(0-index -> 24)
    000000000001000000000000000101000000000000000000
               *                                    press up(0-index -> 11)
    000000000000000000000000000001000000000000010000
                                               *    release up(0-index -> 43)
    000000000010000000000000001001000000000000000000
              *                                     press down
    000000000000000000000000000001000000000000100000
                                              *     release down
        
    000000000000000000000000000000010000000000000000
                                   *                z(shot)(0-index -> 31)
    000000000000000100000000000000010000000000000000
                   *                                press z(0-index -> 15)
    000000000000001000000000000000100000000000000000
                                  *                 x(bomb)(0-index -> 30)
                  *                                 press x(0-index -> 14)
    000000000000010000000000000001000000000000000000
                                 *                  shift(slow move)(0-index -> 29)
                 *                                  press shift(0-index -> 13)
    000000010000000000000001000000000000000000000000
    000000000000000000000000000000000000000100000000
    000000000000000000000000000100000000000000000000
                           ***** ***                pressing ctrl, right, left, down, up, shift,x,z
    000000000001000000000000000101000000000000000000
           ***** ***                                press ctrl, right, left, down, up, shift,x,z
    000000000000000000000000000001000000000000010000
                                           ***** ***release ctrl, right,left,down,up,shift,x,z
    
    '''
    assert len(replay) % 6 == 0
    frame = len(replay) // 6
    l = []
    for i in range(frame):
        # a frame code 8 * 6 = 48 keys would be pressd
        n1,n2 = unpack('IH',replay[i*6:(i+1)*6])
        l.append(bin32(n1) + bin16(n2))
    return l