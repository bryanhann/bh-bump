import subprocess

from .constants import ROOT
from .note import note as NOTE

def wetwrap(func):
    def wrapper_func(*a,**b):
        wet = b['wet']
        del b['wet']
        args = [ repr(x) for x in a ] + [ f"{k}={repr(v)}" for k,v in b.items() ]
        args = ', '.join(args)
        line = f'[{func.__name__}({args})]'
        if wet:
            NOTE( f'wet: {line}' )
            func(*a,**b)
        else:
            NOTE( f'dry: {line}' )
    return wrapper_func

def wetrun(wet, block):
    lines = block.split('\n')
    aa = [ x.strip() for x in lines ]
    bb = [ x for x in aa if x ]
    for line in bb:
        if wet:
            NOTE( f'WET: [{line}]' )
            subprocess.run( line.split() )
        else:
            NOTE( f'DRY: [{line}]' )

def backup(orig):
    tmp = ROOT/'.tmp'
    tmp.exists() or tmp.mkdir()
    aa = map( lambda ii : tmp/f'bak-{orig.name}.{ii}', range(1000) )
    bb = filter( lambda x: not x.exists(), aa )
    bak = next(bb)
    if orig.exists():
        print( f"backing up [{orig.relative_to(ROOT)}] -> [{bak.relative_to(ROOT)}]" )
        bak.write_text( orig.read_text() )
