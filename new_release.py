#!/usr/bin/env python2
from subprocess import call, Popen, PIPE
import argparse

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('--patch', action='store_true', default=True)
	parser.add_argument('--major', action='store_true', default=False)
	parser.add_argument('--minor', action='store_true', default=False)
	return parser.parse_args()

def get_version():
	p = Popen(['git', 'tag'], stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	# Last line is always empty, so take previous
	return stdout.split('\n')[-2].split('.')

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

def main():
	args = get_arguments()
	if args.major:
		version = increase_major()
	elif args.minor:
		version = increase_minor()
	elif args.patch:
		version = increase_patch()
	call (['git', 'tag', version])
	call (['git', 'push', '--tags'])
	call (['python', 'setup.py', 'sdist', 'upload', '-r', 'pypi'])

if __name__=='__main__':
	main()