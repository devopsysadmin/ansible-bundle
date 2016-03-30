#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import yaml
import argparse
import os, sys, time
from subprocess import Popen, STDOUT, PIPE, call

FOLDER = os.getcwd()
PATH = {
	'role' 		: '%s/roles' %FOLDER,
	'library' 	: '%s/library' %FOLDER,
	}

DEFAULT_SCM = 'git'
DEFAULT_SCM_VERSION = 'master'
DEFAULT_SCM_BASE = 'https://descinet.bbva.es/stash/scm'
DEFAULT_SCM_URL = {
	'role'		: '%s/doarol/' %DEFAULT_SCM_BASE,
	'module'	: '%s/doamod/' %DEFAULT_SCM_BASE
	}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Git:
	url = None
	path = None
	tag = None

	def __init__(self, url, path):
		self.url = url
		self.path = path

	def get(self, version):
		cmd = [ 'git','clone', '--branch', version, '--depth', '1', self.url, self.path ]
		stdout, rc = run_cmd(cmd)
		if rc == 0 :
			return True
		else:
			return False

	def branch(self):
		cmd = ['git', 'branch']
		stdout, rc = run_cmd(cmd)
		if rc == 0:
			return stdout.split(' ')[1]
		else:
			raise Exception('Could not get current branch')

	def update(self):
		cmd = ['git', 'pull', 'origin', self.branch() ]
		prev = os.getcwd()
		os.chdir(self.path)
		stdout, rc = run_cmd(cmd)
		os.chdir(prev)
		if rc == 0:
			return True
		else:
			return False


def load_yml(filename):
	with open(filename, 'r') as fn:
		contents = yaml.load(fn)
	return contents

def printf(message, lr=True):
	if lr:
		print message
	else:
		print message,
	sys.stdout.flush()

def run_cmd(command):
	stdout = None
	stderr = None
	process = Popen(command, shell=False, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	output = stdout + stderr
	returncode = process.returncode
	return output, returncode

def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('--file', dest='filename', default='site.yml',
		help='YML file to be processed (default:site.yml)')
	parser.add_argument('--run', action='store_true', dest='run_playbook',
		default=False, 
		help='Runs ansible-playbook with default params after getting bundles')
	parser.add_argument('--runargs', dest='args', nargs='?',
		help='ansible-playbook arguments, if needed. Must be put into quotes')

	return parser.parse_args()


def get_name_and_version_from_bundle_name(bundleName):
	string = bundleName.split('/')
	name = string[0]
	version = string[1] if len(string)>1 else 'master'
	return name, version

def get_bundle_from(bundle, kind):
	b = {
		'name'		: None,
		'kind'		: None,
		'version'	: DEFAULT_SCM_VERSION,
		'src' 		: None,
		'scm'		: DEFAULT_SCM
	}
	if isinstance(bundle, str):
		name, version = get_name_and_version_from_bundle_name(bundle)
		upd = {
			'name': name,
			'version' : version,
			'src' : DEFAULT_SCM_URL[kind] + name,
			'kind': kind
		}
		b.update(upd)
		return b
	elif isinstance(bundle, dict):
		name, version = get_name_and_version_from_bundle_name(bundle[kind])
		upd = {
			'name'	: name,
			'version' : version,
			'src'	: DEFAULT_SCM_URL[kind] + name,
			'kind'	: kind
		}
		b.update(upd)
		b.update(bundle)
		return b
	else:
		return None


def get_all_bundles_in_yml(yml):
	if 'dependencies' in yml:
		itemlist = yml['dependencies']
		sectionlist = ('role', 'library')
	else:
		itemlist = yml
		sectionlist = ('roles', 'libraries')

	bundles = list()
	if len(itemlist)>0:
		for item in itemlist:
			if 'roles' in item:
				for bundle in item['roles']:
					b = get_bundle_from(bundle, 'role')
					bundles.append(b)
			elif 'role' in item:
				bundle = item['role']
				b = get_bundle_from(bundle, 'role')
				bundles.append(b)
			elif 'libraries' in item:
				for bundle in item['libraries']:
					b=get_bundle_from(bundle, 'library')
					bundles.append(b)
			elif 'library' in item:
				bundle = item['library']
				b = get_bundle_from(bundle, 'library')
				bundles.append(b)
			elif 'modules' in item:
				for bundle in item['modules']:
					b = get_bundle_from(bundle, 'library')
					bundles.append(b)
			elif 'module' in item:
				bundle = item['module']
				b = get_bundle_from(bundle, 'library')
				bundles.append(b)

	return bundles


def get_bundle_path(bundle):
	kind = bundle['kind']
	if bundle['version']=='master':
		path = '%s/%s' %(PATH[kind], bundle['name'])
	else:
		path = '%s/%s/%s' %(PATH[kind], bundle['name'], bundle['version'])
	return path


def get_bundle_code(bundle):
	errcode = None
	folder = get_bundle_path(bundle)
	
	scm = {
		'git'	: Git,
	}
	code = scm[bundle['scm']](bundle['src'], folder)
	if os.path.exists(folder):
		msg = 'Updating'
		func = code.update
		args = None
	else:
		msg = 'Getting'
		func = code.get
		args = bundle['version']
	printf ('%s %s from %s (%s)...' %(msg, bundle['name'], bundle['src'], bundle['version']), False)
	ok = func(args) if args else func()

	if ok:
		msg = bcolors.OKGREEN + 'OK' + bcolors.ENDC
	else:
		msg = bcolors.FAIL + 'ERROR' + bcolors.ENDC
	printf(msg)
	return ok


def get_dependencies_tree(root):
	deps = list()
	for (dir, _, filenames) in os.walk(PATH[root]):
		for filename in filenames:
			path = os.path.join(dir, filename)
			if 'meta/main.yml' in path:
				deps += get_all_bundles_in_yml(load_yml(path))

	return deps

def get_includes(yml):
	retList=list()
	for element in yml:
		for key, value in element.items():
			if key == 'include' and value is not None:
				retList += load_yml(value)
	return retList

def main():
	params = get_arguments()
	downloaded=list()

	## End if file doesn't exist
	if not os.path.exists(params.filename):
		return ('File %s not found' %params.filename)

	## Get bundles from YML
	yml = get_includes(load_yml(params.filename))
	for bundle in get_all_bundles_in_yml(yml):
		if bundle not in downloaded:
			get_bundle_code(bundle)
			downloaded.append(bundle)

	## Get bundles from meta/main.yml on each bundle
 	waitlist = ['dummy']
 	while len(waitlist)>0:
 		dependencies = get_dependencies_tree('role') + get_dependencies_tree('library')
 		waitlist = [item for item in dependencies if item not in downloaded]
 		for bundle in waitlist:
			get_bundle_code(bundle)
 			downloaded.append(bundle)

 	if params.run_playbook is True:
		args = params.args.split(' ') if params.args else list()
 		ansible = ['ansible-playbook', params.filename ] + args
 		printf('Running ' + bcolors.BOLD + ' '.join(ansible) + bcolors.ENDC)
 		call(ansible)



########################################################
if __name__ == "__main__":
	sys.exit(main())
