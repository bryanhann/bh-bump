#!/usr/bin/env python3
import argparse
from pathlib import Path
import subprocess
from bh_bump.util import die, name4toml, version4toml, repo_exists

parser = argparse.ArgumentParser(
    prog='ProgramName',
    description='What the program does',
    epilog='Text at the bottom of help'
)
parser.add_argument('root')
parser.add_argument('--user')
parser.add_argument('--public', action='store_true')
OPTS = parser.parse_args()

ROOT = Path(OPTS.root)
DATA = Path(__file__).parent/'data'

class Namespace: pass
C = Namespace
C.VERSION = version4toml( ROOT/'pyproject.toml')
C.PATTERN = 'XXX-current-version-XXX'
C.REPO = name4toml( ROOT/'pyproject.toml' )
C.DST  = ROOT/'.bumpversion.cfg'
C.SRC  = DATA/'bumpversion.cfg'
C.SCRIPT = DATA/'init4repo4user4vis.sh'



def main()
    if C.DST.exists():      die( 1, './.bumpversion.cfg already exists' )
    if repo_exists(C.REPO): die( 2, 'repo already exists' )

    #create_bumpversion_configuration_file
    C.DST.write_text(C.SRC.read_text().replace( C.PATTERN, C.VERSION))

    #initiate_repo
    user=OPTS.user
    while not user:
        user = input('enter github username: ')
    vis = (OPTS.public and '--public') or '--private'

    args = [ C.SCRIPT, C.REPO, user, vis ]
    args = [ str(arg) for arg in args ]
    subprocess.run( args )

if __name__ == '__main__':
    main()
