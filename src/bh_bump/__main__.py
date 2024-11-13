import subprocess
import typer

import bh_bump.toml as TT
import bh_bump.util as UU
import bh_bump.git  as GG
from .note import note as NOTE
from .note import die as DIE
from .constants import GIT, ROOT, CFG_SRC, CFG_DST, CFG_PATTERN, TOML

myapp = typer.Typer()

def assert_in_root_directory():
    if not TOML.exists():
        NOTE("Not found: [./pyproject.toml].")
        NOTE("Are you in the root of your project?")
        DIE(66, 'aborting')

def main():
    assert_in_root_directory()
    myapp()


def _bump(part, wet:bool=False):
    def run(line): UU.wetrun(wet=wet, line=line)
    run( f"uv run bumpversion {part}" )
    run( "uv lock")
    run( "git add uv.lock")
    run( "git commit --amend --no-edit")
    run( "git push")
    run( "git push --tags")

@myapp.command()
def version():
    print( f'{TT.version()}' )

@myapp.command()
def build(wet: bool=True):
    conf_create(); toml_norm(wet); NOTE( f'bumping [build]' )
    _bump( 'build', wet=wet)

@myapp.command()
def release(wet: bool=True):
    conf_create(); toml_norm(wet); NOTE( f'bumping [release]' )
    _bump( 'release', wet=wet)

@myapp.command()
def patch(wet: bool=True):
    conf_create(); toml_norm(wet); NOTE( f'bumping [patch]' )
    _bump( 'patch', wet=wet)
    release( wet )

@myapp.command()
def minor(wet: bool=True):
    conf_create(); toml_norm(wet); NOTE( f'bumping [minor]' )
    _bump( 'minor', wet=wet)
    release( wet )

@myapp.command()
def major(wet: bool=True):
    conf_create(); toml_norm(wet); NOTE( f'bumping [major]' )
    _bump( 'major', wet=wet)
    release( wet )


@myapp.command()
def bump(part, wet: bool=False):
    conf_create()
    toml_norm()
    if part in 'major minor patch'.split():
        NOTE( f'bumping [{part}]' )
        NOTE( 'follow by bumping [release]' )
        _bump('release', wet=wet)
    elif part in 'build release'.split():
        NOTE( f'bumping [{part}]' )
        _bump(part, wet=wet)


@myapp.command()
def bump_init(wet: bool=False, fresh: bool=False):
    conf_create(wet=wet)
    toml_norm(wet=wet)
    git_init(wet=wet, fresh=fresh)
    if not GG.git_has_commit():
        git_init(wet=wet)
    UU.wetrun( wet=wet, line='uv sync' )
    UU.wetrun( wet=wet, line='uv lock' )
    UU.wetrun( wet=wet, line='git add .bumpversion.cfg' )
    UU.wetrun( wet=wet, line='git add pyproject.toml' )
    UU.wetrun( wet=wet, line='git commit -m "first commit"' )
    if TT.repo_exists():
        user = UU.get_username('bryanhann')
        remote = f"git@github.com:{user}/{TT.repo()}.git"
        UU.wetrun( wet=wet, line=f"git remote add origin {remote}" )
        UU.wetrun( wet=wet, line=f"git pull" )

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

@myapp.command()
def stat(all: bool=False):
    """Print status of project

    Here is more help"""
    NOTE( f"git_exists() -> {GG.git_exists()}" )
    NOTE( f"git_has_commit() -> {GG.git_has_commit()}" )
    if not all:
        NOTE( f"repo_exists() -> SKIPPING" )
    else:
        NOTE( f"repo_exists() -> {TT.repo_exists()}" )

@myapp.command()
def repo_create(public: bool=False, wet: bool=False):
    """Create a remote repository for ths project

    """
    TT.repo_exists() and DIE(0, 'repo already exists' )
    vis = (public and '--public') or '--private'
    line = f'gh repo create {TT.repo()} {vis}'
    UU.wetrun( wet=wet, line=line )

@myapp.command()
def repo_delete(wet: bool=False):
    """Delete the remote repository for ths project
    """
    TT.repo_exists() or DIE(0, 'no repo to delete' )
    UU.wetrun( wet=wet, line = f'gh repo delete {TT.repo()}' )

@myapp.command()
def init(wet: bool=True, fresh: bool=False, public=False):
    """Initialse (or reinitialize) [.git]
    """
    toml_norm(wet=wet)
    conf_create()
    TT.repo_exists() and DIE(1, 'remote repo exists')
    fresh and git_delete(wet=wet)
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
    # bumversion gets wonkey if we don't patch first
    bump('patch', wet=wet)

@myapp.command()
def git_delete(wet: bool=False):
    """Delete [.git].

    Useful for testing purposes.
    """
    import shutil
    try:
        UU.wetwrap(shutil.rmtree)(str(GIT), wet=wet)
    except FileNotFoundError:
        NOTE( 'git not found' )

@myapp.command()
def repo_push(wet: bool=False):
    """Push the existing project to the remote repository
    """
    user = UU.get_username('bryanhann')
    remote = f"git@github.com:{user}/{TT.repo()}.git"
    UU.wetrun( wet=wet, line=f"git remote add origin {remote}" )
    UU.wetrun( wet=wet, line=f"git branch -M main" )
    UU.wetrun( wet=wet, line=f"git push -u origin main" )


