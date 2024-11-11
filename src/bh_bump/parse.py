#!/usr/bin/env python3

import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    prog='COMMAND',
    description='What the program does',
    epilog='Text at the bottom of help'
)
parser.add_argument('--user')
parser.add_argument('--public', action='store_true')
parser.add_argument('root')

OPT = parser.parse_args()

def visability():
    return (OPT.public and '--public') or '--private'

def username():
    user = OPT.user
    while not user:
        user = input('enter github username: ')
    return user

def root():
    return Path(OPT.root)
