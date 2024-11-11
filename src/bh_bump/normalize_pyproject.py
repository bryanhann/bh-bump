#!/usr/bin/env python3
from pathlib import Path
import argparse

NL = '\n'
NOTE = " # bh.bump: this line must be first."
def root(): return Path(OPT.root)
def toml(): return root()/'pyproject.toml'

parser = argparse.ArgumentParser(
    prog='NORMALIZE',
    description='What the program does',
    epilog='Text at the bottom of help'
)
parser.add_argument('root')
OPT = parser.parse_args()

def normalize():
    print( f'normalizing {toml()}' )
    bak = backup()
    old = toml().read_text()
    new = new4old(old)
    if new == old:
        return
    bak.write_text( old )
    toml().write_text( new )
    print( f"old pyproject.toml backed up to {bak}" )

def backup():
    for ii in range(100):
        backup = root()/f'tmp.bak.{ii}.pyproject.toml'
        if not backup.exists():
            return backup

def find(lines,target):
    lines = lines[:]
    acc = []
    while lines:
        acc.append(lines.pop(0))
        if acc[-1].startswith( target ):
            return acc, lines

def fix_line(line):
    return line.split('#')[0].strip() + NOTE

def new4old(old):
    xx = old.split(NL)
    aa , xx = find(xx, '[project]')
    bb , xx = find(xx, 'version')
    line = bb.pop(-1)
    line = fix_line(line)
    aa.append( line )
    return NL.join(aa + bb + xx)

if __name__ == '__main__':
    normalize()
