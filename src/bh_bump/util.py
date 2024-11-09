import sys
import os
import tomllib
import json
from subprocess import run
from pathlib import Path


def version4toml(toml):
    with open(toml, "rb") as f:
        return tomllib.load(f)[ 'project' ][ 'version' ]

def name4toml(toml):
    with open(toml, "rb") as f:
        return tomllib.load(f)[ 'project' ][ 'name' ]


def write_config():
    version = version4toml(TOML)
    old = CFG_SRC.read_text()
    new = old.replace( 'XXX-current-version-XXX', version )
    CFG_DST.write_text(new)


def repo_exists(name):
     it = run( 'gh repo list --json name'.split(), capture_output=True)
     names = [ item['name'] for item in json.loads(it.stdout) ]
     return name in names

#!/usr/bin/env python3
def die( code, msg ):
    print(msg)
    exit(code)
