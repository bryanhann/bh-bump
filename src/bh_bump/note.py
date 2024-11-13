import sys

from colorama import Fore, Back, Style

def bold(*items):
    msg = __msg_join(*items)
    return Fore.RED + Style.BRIGHT + msg + Style.RESET_ALL

def note(*aa):
    __stderr( bold( *aa ))

def die( code, *aa ):
    head = f"die[{code}]:"
    note(bold(head, *aa))
    exit(code)

################################################################

def __stderr(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()

def __msg_join(*items):
    return ' '.join( [str(item) for item in items] )

