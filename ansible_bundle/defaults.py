from __future__ import print_function

import sys
import yaml

from os.path import join, isfile
from os import getcwd, getenv

QUIET = 0
VERBOSE = 1
DEBUG = 2
DRY = False
CLEAN = False
RUN = False
OK = 0
ERROR = 1

DOTS = '\n-------------------'

HOME = getenv('HOME')
WORKDIR = getcwd()

# Color + decoration for messages printed on terminal
MESSAGES = {
    'none': (None, None),
    'ok': ('green', 'bold'),
    'info': ('blue', None),
    'warning': ('yellow', None),
    'error': ('red', 'bold'),
    'debug': ('magenta', 'bold')
}

def load(filename):
    if isfile(filename):
        with open(filename, 'r') as fn:
            return yaml.load(fn)

def echo(message, lr=True, typeOf=None):
    if lr:
        end = '\n'
    else:
        end = ' '
    if typeOf:
        color, decoration = defaults.MESSAGES[typeOf]
        msg = Color.text(message, color=color, decoration=decoration)
    else:
        msg = message
    print(msg, end=end)
    sys.stdout.flush()

class Color:
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta' : '\033[95m',
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


class Config:
    SCM = 'git'
    SCM_VERSION = 'master'
    SCM_PREFIX = ''
    SCM_ROLES = ''
    SCM_MODULES = ''
    verbose = QUIET
    dry = False

    def __init__(self):
        yml = self.load()
        if yml is not '':
            self.setvalues(yml)
        else:
            echo('%s not found or incorrect.' % path, typeOf='error')
            sys.exit(ERROR)

    def load(self):
        LOAD_ORDER = (
            join(WORKDIR, 'bundle.cfg'),
            join(HOME, '.ansible', 'bundle', 'bundle.cfg')
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

