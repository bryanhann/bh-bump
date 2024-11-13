#!/usr/bin/env python
import typer

from .note import note as NOTE
from .note import die as DIE

myapp = typer.Typer()

def main():
    from .constants import TOML
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
def init( wet: bool=True, public: bool=False,):
    """Initialse the project.
    """
    from .util import wetrun
    import bh_bump.toml
    repo = bh_bump.toml.repo()
    user = init_gh_user_or_DIE()
    url = f"git@github.com:{user}/{repo}.git"
    vis = (public and '--public') or '--private'

    wetrun( wet, 'git init')

    files_conf()
    files_add_test()
    files_fix_gitignore()

    if not init_git_has_commit():
        NOTE( 'making commit' )
        wetrun( wet, f"""
            uv lock
            git add .
            git commit -m first-commit
            git branch -M main
        """)

    wetrun( wet, f"""
        gh repo create {repo} {vis}
        git remote add origin {url}
        git push -u origin main
    """)

    release()

@myapp.command()
def version(dry = None):
    """Print the version number"""
    from .toml import version
    print(version())

@myapp.command()
def build(wet: bool=True, skip: bool=False):
    """Bump the build number"""
    bump('build', wet=wet, skip=skip)

@myapp.command()
def release(wet: bool=True, skip: bool=False):
    """Bump the release level"""
    bump( 'release', wet=wet, skip=skip)

@myapp.command()
def patch(wet: bool=True, skip: bool=False):
    """Bump the patch number"""
    bump( 'patch', wet=wet, skip=skip)
    release( wet, skip=True )

@myapp.command()
def minor(wet: bool=True, skip: bool=False):
    """Bump the minor number"""
    bump( 'minor', wet=wet, skip=skip)
    release( wet, skip=True )

@myapp.command()
def major(wet: bool=True, skip: bool=False):
    """Bump the major number"""
    bump( 'major', wet=wet, skip=skip)
    release( wet, skip=True )


##########################################################################
#
#  bump_
#
##########################################################################

def bump__pytest_or_DIE(skip: bool=False):
    import subprocess
    if skip:
        NOTE( 'SKIPPING PYTEST' )
    else:
        NOTE( 'RUNNING PYTEST' )
        it = subprocess.run( 'uv run pytest'.split() )
        if not it.returncode == 0:
            DIE(111, "test failed; bump aborted")

def bump(part, wet:bool=True, skip: bool=False):
    from .util import wetrun
    NOTE( f'BUMPING [{part}]' )
    bump__pytest_or_DIE(skip)
    files_conf()
    wetrun( wet, f"""
        uv run bumpversion {part}
        uv lock
        git add uv.lock
        git commit --amend --no-edit
        git push
        git push --tags
        """)

##########################################################################
#
#  init_
#
##########################################################################

def init_gh_user_or_DIE():
    """Return the username of the github account.
    Also: abort if not logged into github.
    Also: abort if repo already exists.
    """
    import subprocess
    from .toml import repo
    it = subprocess.run( 'gh repo list --limit 99999'.split(), capture_output=True, text=True )
    if not it.returncode == 0:
        DIE(101, 'you are not logged into gh')

    pairs = [ x.split()[0].split('/') for x in it.stdout.split('\n')if x.strip() ]
    users = [ x[0] for x in pairs ]
    repos = [ x[1] for x in pairs ]

    if repo()in repos:
        DIE(102, 'remote repo exists man!')

    return users[0]

def init_git_has_commit():
    import subprocess
    line = "git rev-list -n 1 --all"
    it = subprocess.run(line.split(), capture_output=True)
    return bool(it.stdout)

##########################################################################
#
#  files_
#
##########################################################################

def files_conf():
    files_conf_create()
    files_toml_norm()

def files_conf_create():
    """Create an initial [.bumpversion.cfg] file

    It will be configured to use the version found
    in the [pyproject.toml] file.

    It is designed to expect that the "version =" line
    of the pyproject.toml file be the first line in
    the [project] section.
    """
    from .constants import CFG_DST
    from .constants import CFG_SRC
    from .constants import CFG_PATTERN
    from .util import backup
    from .toml import version
    if CFG_DST.exists():
        NOTE( 'BUMPVERSION.CFG: exists' )
    else:
        backup(CFG_DST)
        old = CFG_SRC.read_text()
        new = old.replace( CFG_PATTERN, version() )
        CFG_DST.write_text(new)
        NOTE( 'BUMPVERSION.CFG: created' )

def files_toml_norm():
    """Normalize the [pyproject.toml] file.

    In section [project], move the "version =" line
    to be the first line in the section.

    THis is necessary for [.bumpversion.cfg] to parse it.
    """
    from .util import wetwrap
    from .toml import normalize
    wetwrap(normalize)(wet=True)


def files_fix_gitignore():
    from .constants import GITIGNORE
    from .constants import GITIGNORE_EXTRA
    extra = GITIGNORE_EXTRA.strip()
    target = extra.split('\n')[0]
    text = GITIGNORE.read_text().strip()
    if not target in text:
        GITIGNORE.write_text( text + "\n\n" + extra + "\n\n" )

def files_add_test():
    from .constants import TEST_SRC
    from .constants import TEST_DST
    if not TEST_DST.parent.is_dir():
        TEST_DST.parent.mkdir()
    TEST_DST.write_text(TEST_SRC.read_text())

