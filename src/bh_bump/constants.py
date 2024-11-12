import os
from pathlib import Path

FILES = Path(__file__).parent/'data'
ROOT = Path(os.getcwd())
TOML = ROOT/'pyproject.toml'
SCRIPT = str(FILES/'init4repo4user4vis.sh')
CFG_PATTERN = "XXX-current-version-XXX"
CFG_SRC = FILES/'bumpversion.cfg'
CFG_DST = ROOT/'.bumpversion.cfg'
GIT = ROOT/'.git'