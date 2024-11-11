#!/usr/bin/env python3

import subprocess

from .util import die, repo_exists
from .parse import visability, username
from .config import repo, version, src, dst, script

def main():
    dst().exists() and die( 1, 'cfg already exists' )
    old = src().read_text()
    new = old.replace( 'XXX-current-version-XXX', version() )
    dst().write_text( new )
    repo_exists(repo()) and die( 2, 'repo already exists' )
    subprocess.run( [ script(), repo(), username(), visability() ] )

if __name__ == '__main__':
    main()
