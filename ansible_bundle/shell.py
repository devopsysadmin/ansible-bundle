#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

from __future__ import print_function
import os
import sys
from subprocess import Popen, PIPE
from subprocess import call as Call
import yaml
import shutil

# Color + decoration for messages printed on terminal
MESSAGES = {
    'none': (None, None),
    'ok': ('green', None),
    'info': ('blue', None),
    'warning': ('yellow', None),
    'error': ('red', 'bold'),
}


class Color:
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
    }

    DECORATIONS = {
        'bold': '\033[1m',
        'underline': '\033[4m',
    }

    END = '\033[0m'

    @classmethod
    def text(cls, s, **kwargs):
        msg = ''
        color = kwargs.get('color', None)
        decoration = kwargs.get('decoration', None)
        if decoration is not None:
            msg += cls.DECORATIONS[decoration]
        if color is not None:
            msg += cls.COLORS[color]
        msg += s
        if color or decoration:
            msg += cls.END
        return (msg)


class Defaults:
    SCM = 'git'
    SCM_VERSION = 'master'
    SCM_PREFIX = ''
    SCM_ROLES = ''
    SCM_MODULES = ''
    VERBOSITY = 0

    def __init__(self):
        yml = self.load()
        if yml is not '':
            self.setvalues(yml)
        else:
            raise Exception('%s not found or incorrect.' % path)

    def load(self):
        LOAD_ORDER = (
            path(pwd(), 'bundle.cfg'),
            path(HOME, '.ansible', 'bundle', 'bundle.cfg')
        )
        for filename in LOAD_ORDER:
            if isfile(filename):
                return load(filename)

    def setvalues(self, yml):
        for key, value in yml.items():
            setattr(self, key, value)
        if self.SCM_PREFIX:
            self.SCM_ROLES = self.SCM_PREFIX + self.SCM_ROLES
            self.SCM_MODULES = self.SCM_PREFIX + self.SCM_MODULES


def load(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as fn:
            return yaml.load(fn)


def echo(message, lr=True, typeOf=None):
    if lr:
        end = '\n'
    else:
        end = ' '
    if typeOf:
        color, decoration = MESSAGES[typeOf]
        msg = Color.text(message, color=color, decoration=decoration)
    else:
        msg = message
    print(msg, end=end)
    sys.stdout.flush()


def run(command, verbose=0):
    if verbose > 0:
        print('\n[DEBUG IN]\n', ' '.join(command), '\n-------------------')
    process = Popen(command, shell=False, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    output = stdout + stderr
    returncode = process.returncode
    if verbose > 0:
        print ('\n[DEBUG OUT]\n', output, '\n-------------------')
    return output, returncode


def pwd():
    return os.getcwd()


def exit(arg):
    return sys.exit(arg)


def isfile(filename):
    return os.path.isfile(filename)


def isdir(dirname):
    return os.path.exists(dirname)


def path(*args):
    return os.path.join(*args)


def call(args):
    return Call(args)


def walk(args):
    return os.walk(args)


def cd(dirname, verbose=0):
    retval = os.chdir(dirname)
    if retval and verbose > 0:
        print('[DEBUG]: Current dir is %s' %dirname)
    return retval

def rmdir(dirname):
    if os.path.exists(dirname):
        try:
            shutil.rmtree(dirname)
            return True
        except:
            return False
    else:
        return True


###############################
OK = 0
ERROR = 1
HOME = os.getenv('HOME')
DEFAULTS = Defaults()
WORKDIR = os.getcwd()
