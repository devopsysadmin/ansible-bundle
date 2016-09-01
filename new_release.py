#!/usr/bin/env python2
from subprocess import call, Popen, PIPE
from ansible_bundle import __version__
import argparse
import os

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('--patch', action='store_true', default=True)
	parser.add_argument('--major', action='store_true', default=False)
	parser.add_argument('--minor', action='store_true', default=False)
	return parser.parse_args()

def get_version():
	return __version__.split('.')

def increase(string):
	return str(int(string)+1)

def increase_patch():
	major, minor, patch = get_version()
	patch = increase(patch)
	return '%s.%s.%s' %(major, minor, patch)

def increase_minor():
	major, minor, patch = get_version()
	minor = increase(minor)
	return '%s.%s.0' %(major, minor)

def increase_major():
	major, minor, patch = get_version()
	major = increase(major)
	return '%s.0.0' %major

def new_version(version):
	filename = os.path.join('ansible_bundle', '__init__.py')
	contents = list()
	newcontents = list()
	with open(filename, 'r') as fn:
		contents = fn.read().split('\n')
	with open(filename, 'w') as fn:
		for line in contents:
			if '__version__' in line:
				fn.write('__version__ = %s' %version)
			else:
				fn.write(line)
			fn.write('\n')

def main():
	args = get_arguments()
	if args.major:
		version = increase_major()
	elif args.minor:
		version = increase_minor()
	elif args.patch:
		version = increase_patch()
	new_version(version)

	script = (
		[ 'git', 'commit', '-am', 'New version %s' %version ],
		[ 'git', 'push'],
		[ 'git', 'tag', version ],
		[ 'git', 'push', '--tags' ],
		[ 'python', 'setup.py', 'sdist', 'upload', '-r', 'pypi' ]
		)
	for line in script:
		call(line)

if __name__=='__main__':
	main()