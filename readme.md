# Touhou project replay file decoder

The project is alomst a Python implementation for [threp](https://github.com/Fluorohydride/threp) by Fluorohydride.
But it include more flexiable API and bug fix (and more slow! Thanks Python).

It support th10(東方風神録　～ Mountain of Faith) and th11(東方地霊殿　～ Subterranean Animism), 
while `threp` support more game, my own statistical only need this two so I have not port others.

## API

### `API.py`

`cut_scan(origin_dir, target_dir)` will transform all `*.rpy` files included in `origin_dir` to python pickled file into `target_dir`.

Every pickled file represents a dictionary, you can use `pickle.load(pickle_file_path)` to load it:

```
with open(your_pickle_path, 'rb') as f:
    info = pickle.load(f)
```

#### Attributions

* `info['stages']`: How many stages replay include.
* `info['character'],info['ctype'],info['rank'],info['clear']`: In a th10 replay, (0,0,0,8) means 
   that it's a `Reimu` `A` play in a `easy` `whole`(so not the extra) game. For detail you can check `th10.th10type` and `th11.th11type`.
* `info['code']`: Indicate what the replay come from, `0x72303174` for th10, and `0x72313174` for th11.
* `info['meta']`: The binary data of the header of the decoded replay file.
* `info['stages']`: is a dictionary, info['stages'][0] is a another dictionary correspond to first stage 
   included in the replay. 
   
```   
stage = info['stages'][0]
```

* `stage['score']`: the score got in this stage.
* `stage['frame']`: the number of frames in the stage.
* `stage['llength']`: the replay section binary data length in the stage.
* `stage['index']`: indicate the index of start and end of the three parts(header,replay,tail) in this stage.
* `stage['bin']`: Dictionary. The binary data part of the stage.

```
replay = stage['bin']['replay']
replay[:100]
#bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00@\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00P\x00\x10\x00\x00\x00P\x00\x00\x00\x00\x00P\x00\x00\x00\x00\x00P\x00\x00\x00')
```

The `replay` is a sequence consist of binary blocks(per frame), every block coded into 6 bytes.

```
from utils import replay_to_binary_seq
seq = replay_to_binary_seq(replay)
seq[10:20]
'''
['000000000000000000000000010000000000000000000000',
 '000000000000000000000000010000000000000000000000',
 '000000000000000000000000010000000000000000000000',
 '000000000001000000000000010100000000000000000000',
 '000000000000000000000000010100000000000000000000',
 '000000000000000000000000010100000000000000000000',
 '000000000000000000000000010100000000000000000000',
 '000000000000000000000000010100000000000000000000',
 '000000000000000000000000010100000000000000000000',
 '000000000000000000000000010100000000000000000000']
'''
```

The 48 bits record the keyboard state in that frame:

```
    000000000000000000000000000100000000000000000000
                           ***** ***                pressing ctrl, right, left, down, up, shift,x,z
    000000000001000000000000000101000000000000000000
           ***** ***                                press ctrl, right, left, down, up, shift,x,z
    000000000000000000000000000001000000000000010000
                                           ***** ***release ctrl, right,left,down,up,shift,x,z
```

For detail, you can check the document string of `replay_to_binary_seq` included in `utils.py`.