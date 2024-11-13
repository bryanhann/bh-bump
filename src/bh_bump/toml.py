#!/usr/bin/env python3
import tomllib

from .constants import TOML
from .util import backup
from .note import note as NOTE

def repo():
    return __loaded()[ 'project' ][ 'name' ]

def version():
    return __loaded()[ 'project' ][ 'version' ]

def normalize():
    NOTE( f'normalizing {TOML}' )
    old = TOML.read_text()
    new = __new4old(old)
    if not new == old:
        backup(TOML)
        TOML.write_text( new )
        NOTE( f"modified.")
    else:
        NOTE( f"no modification needed.")

########################################################

def __loaded():
    with open(TOML, "rb") as f:
        return tomllib.load(f)


def __find(lines,target):
    lines = lines[:]
    acc = []
    while lines:
        acc.append(lines.pop(0))
        if acc[-1].startswith( target ):
            return acc, lines

def __fix_line(line):
    note = " # bh.bump: this line must be first."
    return line.split('#')[0].strip() + note

def __new4old(old):
    NL = '\n'
    xx = old.split(NL)
    aa , xx = __find(xx, '[project]')
    bb , xx = __find(xx, 'version')
    line = bb.pop(-1)
    line = __fix_line(line)
    aa.append( line )
    return NL.join(aa + bb + xx)

