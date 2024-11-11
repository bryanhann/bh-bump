import tomllib
from pathlib import Path

from .parse import root


def src():     return _data()/'bumpversion.cfg'
def dst():     return root()/'.bumpversion.cfg'
def repo():    return _loaded()[ 'project' ][ 'name' ]
def version(): return _loaded()[ 'project' ][ 'version' ]
def script():  return str(_data()/'init4repo4user4vis.sh')
def toml():    return root()/'pyproject.toml'

# Private

def _data():    return Path(__file__).parent/'data'

def _loaded():
    with open(toml(), "rb") as f:
        return tomllib.load(f)

