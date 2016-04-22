#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import os, sys, time
from subprocess import Popen, STDOUT, PIPE
from subprocess import call as Call
import yaml

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Defaults:
	SCM = 'git'
	SCM_VERSION = 'master'
	SCM_PREFIX = ''
	SCM_ROLES = ''
	SCM_MODULES = ''

	def __init__(self):
		yml = self.load()
		if yml is not '':
			self.setvalues(yml)
		else:
			raise Exception('%s not found or incorrect.' %path)

	def load(self):
		LOAD_ORDER=(
			path(pwd(), 'bundle.cfg'),
			path(HOME, '.ansible', 'bundle', 'bundle.cfg' )
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
	contents = None
	if os.path.isfile(filename):
		with open(filename, 'r') as fn:
			contents = yaml.load(fn)
	if contents is None: contents = ''
	return contents

def echo(message, lr=True):
	if lr:
		print message
	else:
		print message,
	sys.stdout.flush()

def run(command):
	stdout = None
	stderr = None
	process = Popen(command, shell=False, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	output = stdout + stderr
	returncode = process.returncode
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
	return os.chdir(dirname)

OK = 0
ERROR = 1
HOME = os.getenv('HOME')
DEFAULTS = Defaults()
WORKDIR = os.getcwd()
