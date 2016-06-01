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
import defaults

Color = defaults.Color
OK = defaults.OK
ERROR = defaults.ERROR
HOME = defaults.HOME
WORKDIR = defaults.WORKDIR

config = defaults.Config()

def load(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as fn:
            return yaml.load(fn)


def echo(message, lr=True, typeOf=None, stderr=False):
    if lr:
        end = '\n'
    else:
        end = ''
    if typeOf:
        color, decoration = defaults.MESSAGES[typeOf]
        msg = Color.text(message, color=color, decoration=decoration)
    else:
        msg = message
    if stderr:
        print(msg, end=end, file=sys.stderr)
    else:
        print(msg, end=end)
    sys.stdout.flush()

def echo_debug(message):
    echo('[DEBUG] ', lr=False, typeOf='debug')
    echo(message, lr=True)

def echo_error(message):
    echo('[ERROR] %s' %message, typeOf='error', stderr=True)

def echo_info(message, lr=False):
    echo('[INFO] %s' %message, typeOf='info', lr=lr)

def echo_warning(message):
    echo('[WARN] %s' %message, typeOf='warning')

def run(command):
    if config.verbose >= defaults.DEBUG:
        echo_debug('IN:\n' + ' '.join(command)+'\n')
    if config.dry is False:
        process = Popen(command, shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        output = stdout + stderr
        returncode = process.returncode
    else:
        output, returncode = ('OK', 0)
    if config.verbose >= defaults.DEBUG:
        echo_debug ('OUT:\n' + output + defaults.DOTS)
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


def cd(dirname):
    try:
        os.chdir(dirname)
        retval=True
    except:
        retval=False

    if retval and config.verbose >= defaults.DEBUG:
        echo_debug('Current dir is ' + dirname + defaults.DOTS)
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
