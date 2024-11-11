import json
import subprocess

def repo_exists(name):
     args = 'gh repo list --json name'.split()
     it = subprocess.run( args, capture_output=True)
     names = [ item['name'] for item in json.loads(it.stdout) ]
     return name in names

def die( code, msg ):
    print(msg)
    exit(code)

