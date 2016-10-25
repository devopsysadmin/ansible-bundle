from __future__ import print_function
from configparser import ConfigParser
from ansible_bundle import worker
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
DEFAULT_URL = 'https://github.com'

# Color + decoration for messages printed on terminal


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

MESSAGES = {
    'none': (None, None),
    'ok': ('green', 'bold'),
    'info': ('blue', None),
    'warning': ('yellow', None),
    'error': ('red', 'bold'),
    'debug': ('magenta', 'bold')
}

END = '\033[0m'

def load_cfg(filename):
    try:
        config = ConfigParser()
        config.read(filename)
        return config
    except:
        sys.exit('Cannot load %s' %filename)


def text(s, **kwargs):
    msg = ''
    color = kwargs.get('color', None)
    decoration = kwargs.get('decoration', None)
    if decoration is not None:
        msg += DECORATIONS[decoration]
    if color is not None:
        msg += COLORS[color]
    msg += s
    if color or decoration:
        msg += END
    return (msg)

def _to_bool(string):
    default = False
    if isinstance(string, bool):
        return string
    elif isinstance(string, str):
        if string.lower() in ('true'):
            return True
        else:
            return False
    return default

class Config:
    SCM = 'git'
    SCM_VERSION = 'master'
    url = DEFAULT_URL
    verbosity = QUIET
    dry = False
    colorize = True
    workers = 1
    pool = None
    safe = False

    def __init__(self):
        pass

    def initialize(self, **kwargs):

        ### First, load the ansible.cfg values
        cfg = self.load()
        if cfg and cfg.has_section('bundle'):
            for key, value in cfg.items('bundle'):
                setattr(self, key, value)
        
        for string in ('workers', 'verbosity'):
            ## The following values should be integer, not string
            setattr(self, string, int(getattr(self, string)))

        for string in ('safe',):
            ## The following values should be boolean, not string
            setattr(self, string, _to_bool(getattr(self, string)))

        ### Then, the args bypassed by command line
        for name, value in kwargs.items():
            if value: setattr(self, name, value)

        self.pool = worker.ThreadPool(self.workers)


    def load(self):
        LOAD_ORDER = (
            join(WORKDIR, 'ansible.cfg'),
            join(HOME, '.ansible.cfg'),
            join('etc', 'ansible', 'ansible.cfg')
        )
        if getenv('ANSIBLE_CONFIG') is not None:
            return load_cfg(os.getenv('ANSIBLE_CONFIG'))
        else:
            for filename in LOAD_ORDER:
                if isfile(filename):
                    return load_cfg(filename)
        return None
