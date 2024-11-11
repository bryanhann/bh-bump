import subprocess

from .constants import  GIT

def git_has_commit():
    line = "git rev-list -n 1 --all"
    it = subprocess.run(line.split(), capture_output=True)
    return bool(it.stdout)

def git_exists():
    return GIT.exists()

