# commands for calling scripts outside this repo
################### (this file is very bad) + do with subprocess

import os

def vcdim_cmd(filename : str) -> int:
    """ works, but prints everything --- do with subprocess """
    stream = os.popen(f'../graph-vcdim/_build/main vcdim {filename}')
    lines = stream.readlines()
    res = int(lines[-1])
    return res


