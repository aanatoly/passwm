#!/usr/bin/python

'''
Simple console password manager 
'''

prog_name = "passwm"
prog_version = "0.1"  # also update version in setup.py
prog_epilog = '''
Example:
   %(prog)s -i all
   %(prog)s -p github
'''


############################################
# Imports
############################################

import logging
import argparse
import json
import os
import sys
import signal
import time


############################################
# Logging
############################################

try:
    # Module logging_conf should intialize root logger and, perhaps some
    # others, and assign 'log' variable to proper logger.
    from logging_conf import log
except:
    log = logging.getLogger()
    log.setLevel(logging.WARNING)
    # log.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    # f = MyFormatter()
    f = logging.Formatter()
    h.setFormatter(f)
    log.addHandler(h)


############################################
# Argument parsing
############################################

p = argparse.ArgumentParser(
    prog=prog_name,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=__doc__,
    epilog=prog_epilog)
p.add_argument("--debug", help="debug mode",
               dest='debug', action="store_true")
p.add_argument("--version", action='version',
               version='%(prog)s ' + prog_version)
p.add_argument("-v", help="verbose mode",
               dest='verbose', action="store_true")

p.add_argument('--init',
               help='Initialize a password safe',
               dest='init',
               action='store_true')
p.add_argument('-a',
               help='Add new entry',
               dest='create',
               action='store_true')
p.add_argument('-u',
               help='Update an entry',
               dest='delete',
               action='store_true')
p.add_argument('-d',
               help='Delete an entry',
               dest='delete',
               action='store_true')
p.add_argument('-i',
               help='Print alias info',
               dest='print_info',
               action='store_true')
p.add_argument('-p',
               help='Print alias password',
               dest='print_info',
               action='store_true')
p.add_argument('alias',
               help='Alias name or "all"',
               nargs='?')


args = p.parse_args()

if args.verbose:
    log.setLevel(logging.INFO)
if args.debug:
    log.setLevel(logging.DEBUG)

log.debug("Args: %s", json.dumps(vars(args), indent=4, sort_keys=True))

############################################
# Misc
############################################

def mkdir_p(path):
    path = os.path.expanduser(path)
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == os.errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
    return path


def signal_handler(signal, frame):
    print
    sys.exit(1)


############################################
# Main
############################################

def main():
    signal.signal(signal.SIGINT, signal_handler)
    objs = []
    ifaces = []
    for d in args.defs:
        load_json(d, objs, ifaces)


if __name__ == '__main__':
    main()
