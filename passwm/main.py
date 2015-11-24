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
import tempfile
import getpass
import subprocess as sp
import string
import random

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
               dest='add',
               action='store_true')
p.add_argument('-u',
               help='Update an entry',
               dest='update',
               action='store_true')
p.add_argument('-d',
               help='Delete an entry',
               dest='delete',
               action='store_true')
p.add_argument('-i',
               help='Print alias info',
               dest='info',
               action='store_true')
p.add_argument('-p',
               help='Print alias password',
               dest='info_password',
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
# Safe
############################################

class Safe(object):
    def_dir = '~/.config/passwm'

    def __init__(self, password='', path=''):
        if not self.env_is_ok():
            print "Please install gpg 2.x version"
            exit(100)

        if not password:
            password = getpass.getpass('Enter master password: ')
        self.password = password
        log.debug("password: '%s'", self.password)

        if not path:
            path = os.path.expanduser(self.def_dir)
            mkdir_p(path)
            path += '/safe.gpg'
        self.path = path
        log.debug("path: '%s'", self.path)

        self.data = {}
        self.null = open('/dev/null', 'w')

    def env_is_ok(self):
        cmd = 'gpg --version'.split()
        try:
            text = sp.check_output(cmd)
            # the output is "gpg (GnuPG) 2.0.28", so we need
            # last token of a first line
            text = text.splitlines()[0].split()[-1]
            log.debug("gpg version %s", text)
            return text.startswith('2.')
        except:
            pass
        return False

    def get_cmd(self, action, name):
        if action == 'encrypt':
            cmd = 'gpg -q --symmetric --armor --batch --yes '
            cmd += '--passphrase-file %s --output'
            cmd = cmd % name
        elif action == 'decrypt':
            cmd = 'gpg -q --decrypt   --no-mdc-warning --batch --armor '
            cmd += '--passphrase-file %s'
            cmd = cmd % name
        else:
            raise Exception("bad action")
        cmd = cmd.split() + [self.path]
        log.debug("cmd '%s'", ' '.join(cmd))
        return cmd

    def validate_alias(self, action, alias, allow_all=False):
        if not alias:
            print action, "command require an alias."
            exit(100)
        if alias == 'all' and not allow_all:
            print "Can't", action, "'all' alias. Use another name."
            exit(100)

    def generate_password(self, length):
        chars = string.ascii_letters + string.digits
        s = ''.join([random.choice(chars) for _ in range(length)])
        return s

    def read(self):
        try:
            with tempfile.NamedTemporaryFile(mode='w+b') as tmp:
                tmp.write(self.password)
                tmp.flush()

                cmd = self.get_cmd("decrypt", tmp.name)
                st_out = sp.check_output(cmd)
                self.data = json.loads(st_out)
                log.debug("json %s", json.dumps(self.data, indent=4))
        except:
            print
            print "Did you ran '%s --init' ?" % prog_name
            exit(100)

    def write(self):
        with tempfile.NamedTemporaryFile(mode='w+b') as tmp:
            tmp.write(self.password)
            tmp.flush()

            cmd = self.get_cmd("encrypt", tmp.name)
            job = sp.Popen(cmd, stdin=sp.PIPE)
            job.communicate(json.dumps(self.data))
            log.debug("write rc %d", job.returncode)

    def add(self, alias):
        self.validate_alias('add', alias)
        if alias in self.data:
            print "Alias", alias, "already exists"
            exit(100)
        self.data[alias] = {'alias': alias}
        self.update(alias)

    def update(self, alias):
        self.validate_alias('update', alias)
        try:
            a = self.data[alias]
        except:
            print "Alias '%s' does not exists" % alias
            exit(100)

        # access times
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        if 'created' not in a:
            a['created'] = now
        a['modified'] = now

        # username
        username = raw_input('Enter the account name (username/email/etc): ')
        username = username.strip()
        if not username:
            print "No username"
            exit(100)
        a['username'] = username

        # password
        gen_password = raw_input('Generate random password? [Y/n]: ')
        if gen_password.strip() in ['n', 'N']:
            password = getpass.getpass('Enter the password: ')
            password = password.strip()
            if not password:
                print "No password"
                exit(100)
        else:
            password = self.generate_password(20)
        a['password'] = password

    def delete(self, alias):
        self.validate_alias('delete', alias)
        try:
            del self.data[alias]
        except:
            print "Alias '%s' does not exists" % alias
            exit(100)

    def info(self, alias):
        self.validate_alias('info', alias, allow_all=True)
        if alias == 'all':
            aliases = sorted(self.data.keys())
        else:
            aliases = [aliases]
        for a in aliases:
            print "alias '%s'" % a
            a = self.data[a]
            for key in ['username', 'password', 'created', 'modified']:
                print "  %10s : %s" % (key, a[key])
            print

############################################
# Main
############################################


def main():
    signal.signal(signal.SIGINT, signal_handler)

    s = Safe()

    if args.init:
        s.write()
        exit(0)

    s.read()
    if args.info:
        s.info(args.alias)
        exit(0)

    if args.add:
        s.add(args.alias)
    elif args.update:
        s.update(args.alias)
    elif args.delete:
        s.delete(args.alias)
    else:
        # bad command ?
        pass
    s.write()


if __name__ == '__main__':
    main()
