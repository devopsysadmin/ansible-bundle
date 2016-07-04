#!/usr/bin/env python2
from subprocess import call, Popen, PIPE
import argparse

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('--patch', action='store_true', default=False)
	parser.add_argument('--major', action='store_true', default=False)
	parser.add_argument('--minor', action='store_true', default=False)
	return parser.parse_args()

def get_version():
	p = Popen(['git', 'tag'], stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	stdout.split('\n')[-2] # Last line is always empty, so take previous
	return version.split('.')

def increase(pos):
	version = get_version()
	version[pos] = str(int(version[pos])+1)
	return '%s.%s.%s' %(version[0], version[1], version[2])

def main():
	args = get_arguments()
	if args.major:
		version = increase(0)
	elif args.minor:
		version = increase(1)
	else:
		version = increase(2)
	call (['git', 'tag', version])
	call (['git', 'push', '--tags'])
	call (['python', 'setup.py', 'sdist', 'upload', '-r', 'pypi'])

if __name__=='__main__':
	main()