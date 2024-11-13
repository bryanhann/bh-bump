import subprocess
import os
from pprint import pprint

import typer

import bh_bump.toml as TT
import bh_bump.util as UU
from .note import note as NOTE
from .note import die as DIE
from .constants import GIT, ROOT, CFG_SRC, CFG_DST, CFG_PATTERN, TOML
from .constants import TEST_SRC, TEST_DST

myapp = typer.Typer()

def main():
    if not TOML.exists():
        NOTE("Not found: [./pyproject.toml].")
        NOTE("Are you in the root of your project?")
        DIE(66, 'aborting')
    myapp()

##########################################################################
#
#  User commands: init, build, release, patch, minor, major
#
##########################################################################
def _add_test():
    if not TEST_DST.parent.is_dir():
        TEST_DST.parent.mkdir()
    TEST_DST.write_text(TEST_SRC.read_text())
@myapp.command()
def add_test():
    print(TEST_DST)
    if not TEST_DST.parent.is_dir():
        TEST_DST.parent.mkdir()
    TEST_DST.write_text(TEST_SRC.read_text())

@myapp.command()
def init(
    wet:    bool=True,
    public: bool=False,
    ):
    """Initialse the project.
    """
    user = _gh_user()
    repo = TT.repo()
    url = f"git@github.com:{user}/{repo}.git"
    vis = (public and '--public') or '--private'

    toml_norm()
    conf_create()

    UU.wetrun( wet=wet, line=f'git init' )
    _add_test()

    if not _git_has_commit():
        NOTE( 'making commit' )
        UU.wetrun( wet, f'uv lock'                          )
        UU.wetrun( wet, f'git add {TOML} {CFG_DST} uv.lock' )
        UU.wetrun( wet, f'git commit -m first-commit'       )
        UU.wetrun( wet, f'git branch -M main'               )
    UU.wetrun( wet, f'gh repo create {repo} {vis}' )
    UU.wetrun( wet, f'git remote add origin {url}' )
    UU.wetrun( wet, f'git push -u origin main'     )

    # bumpversion gets wonkey if we don't release first
    release()

@myapp.command()
def version():
    """Print the current version of the project"""
    print( f'{TT.version()}' )

@myapp.command()
def build(wet: bool=True, test: bool=True):
    """Bump the build number"""
    _bump('build', wet=wet, test=test)

@myapp.command()
def release(wet: bool=True, test: bool=True):
    """Bump the release level"""
    _bump( 'release', wet=wet, test=test)

@myapp.command()
def patch(wet: bool=True, test: bool=True):
    """Bump the patch number"""
    _bump( 'patch', wet=wet, test=test)
    release( wet, test=False )

@myapp.command()
def minor(wet: bool=True, test: bool=True):
    """Bump the minor number"""
    _bump( 'minor', wet=wet, test=test)
    release( wet, test=False )

@myapp.command()
def major(wet: bool=True, test: bool=True):
    """Bump the major number"""
    _bump( 'major', wet=wet, test=test)
    release( wet, test=False )

##########################################################################
#
#  Internal commands.
#
##########################################################################

@myapp.command()
def toml_norm( wet: bool=False):
    """Normalize the [pyproject.toml] file.

    In section [project], move the "version =" line
    to be the first line in the section.

    THis is necessary for [.bumpversion.cfg] to parse it.
    """

    UU.wetwrap(TT.normalize)(wet=True)

@myapp.command()
def conf_create():
    """Create an initial [.bumpversion.cfg] file

    It will be configured to use the version found
    in the [pyproject.toml] file.

    It is designed to expect that the "version =" line
    of the pyproject.toml file be the first line in
    the [project] section.
    """

    if CFG_DST.exists():
        NOTE( 'BUMPVERSION.CFG: exists' )
        return
    UU.backup(CFG_DST)
    old = CFG_SRC.read_text()
    new = old.replace( CFG_PATTERN, TT.version() )
    CFG_DST.write_text(new)
    NOTE( 'BUMPVERSION.CFG: created' )


def _run_pytest():
    it = subprocess.run( 'uv run pytest'.split() )
    if not it.returncode == 0:
        DIE(111, "test failed; bump aborted")

def _bump(part, wet:bool=True, test: bool=True):
    NOTE( f'BUMPING [{part}]' )
    if test:
        NOTE( 'RUNNING PYTEST' )
        _run_pytest()
    else:
        NOTE( 'SKIPPING PYTEST' )

    conf_create();
    toml_norm(wet);

    def run(line): UU.wetrun(wet=wet, line=line)
    run( f"uv run bumpversion {part}" )
    run( "uv lock")
    run( "git add uv.lock")
    run( "git commit --amend --no-edit")
    run( "git push")
    run( "git push --tags")

def _gh_user():
    """Return the username of the github account.
    Also: abort if not logged into github.
    Also: abort if repo already exists.
    """
    myrepo = TT.repo()

    it = subprocess.run( 'gh repo list --limit 99999'.split(), capture_output=True, text=True )
    if not it.returncode == 0:
        DIE(101, 'you are not logged into gh')

    pairs = [ x.split()[0].split('/') for x in it.stdout.split('\n')if x.strip() ]
    users = [ x[0] for x in pairs ]
    repos = [ x[1] for x in pairs ]

    if myrepo in repos:
        DIE(102, 'remote repo exists man!')

    return users[0]


def _git_has_commit():
    line = "git rev-list -n 1 --all"
    it = subprocess.run(line.split(), capture_output=True)
    return bool(it.stdout)


