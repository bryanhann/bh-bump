import subprocess
import typer

import bh_bump.toml as TT
import bh_bump.util as UU
import bh_bump.git  as GG
from .note import note as NOTE
from .note import die as DIE
from .constants import GIT, ROOT, CFG_SRC, CFG_DST, CFG_PATTERN, TOML

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

@myapp.command()
def init(wet: bool=True, public=False):
    """Initialse the project.
    """
    def repo_create(public: bool=False, wet: bool=False):
        TT.repo_exists() and DIE(0, 'repo already exists' )
        vis = (public and '--public') or '--private'
        line = f'gh repo create {TT.repo()} {vis}'
        UU.wetrun( wet=wet, line=line )
    toml_norm(wet=wet)
    conf_create()
    TT.repo_exists() and DIE(1, 'remote repo exists')
    UU.wetrun( wet=wet, line=f'git init' )
    if not GG.git_has_commit():
        NOTE( 'making commit' )
        UU.wetrun( wet=wet, line=f'uv lock' )
        UU.wetrun( wet=wet, line=f'git add {TOML}' )
        UU.wetrun( wet=wet, line=f'git add {CFG_DST}' )
        UU.wetrun( wet=wet, line=f'git add uv.lock' )
        UU.wetrun( wet=wet, line='git commit -m first-commit' )
        UU.wetrun( wet=wet, line='git branch -M main' )
    repo_create(wet=wet, public=public)
    user = UU.get_username('bryanhann')
    repo = TT.repo()
    url = f"git@github.com:{user}/{repo}.git"
    UU.wetrun( wet=wet, line=f"git remote add origin {url}")
    UU.wetrun( wet=wet, line=f"git push -u origin main")
    # bumpversion gets wonkey if we don't release first
    release()

@myapp.command()
def version():
    """Print the current version of the project"""
    print( f'{TT.version()}' )


@myapp.command()
def build(wet: bool=True):
    """Bump the build number"""
    _bump( 'build', wet=wet)

@myapp.command()
def release(wet: bool=True):
    """Bump the release level"""
    _bump( 'release', wet=wet)

@myapp.command()
def patch(wet: bool=True):
    """Bump the patch number"""
    _bump( 'patch', wet=wet)
    release( wet )

@myapp.command()
def minor(wet: bool=True):
    """Bump the minor number"""
    _bump( 'minor', wet=wet)
    release( wet )

@myapp.command()
def major(wet: bool=True):
    """Bump the major number"""
    _bump( 'major', wet=wet)
    release( wet )

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
        NOTE( '.bumpversion.cfg already exists' )
        return
    UU.backup(CFG_DST)
    old = CFG_SRC.read_text()
    new = old.replace( CFG_PATTERN, TT.version() )
    if old == new:
        NOTE('cfg unchanged')
    else:
        CFG_DST.write_text(new)
        NOTE('cfg updated')



def _bump(part, wet:bool=False):
    conf_create();
    toml_norm(wet);
    NOTE( f'bumping [{part}]' )
    def run(line): UU.wetrun(wet=wet, line=line)
    run( f"uv run bumpversion {part}" )
    run( "uv lock")
    run( "git add uv.lock")
    run( "git commit --amend --no-edit")
    run( "git push")
    run( "git push --tags")


