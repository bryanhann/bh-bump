#!/usr/bin/env python
from os.path import splitext
import subprocess
BASE = splitext(__file__)[0]

def test():
    it = subprocess.run( BASE + '.sh'  )
    assert it.returncode == 0
