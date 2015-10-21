#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import yaml
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
	'role'		: '%s/doansr/' %DEFAULT_SCM_BASE,
	'module'	: '%s/doansm/' %DEFAULT_SCM_BASE
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
	branch = None
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
			errorlist.append('git %s: %s' %(self.url, self.error(rc)))
			return False

	def error(self, errcode):
		msg = {
			128	: 'Repository does not exist'
		}
		return msg[errcode]


def load_yml(filename):
	with open(filename, 'r') as fn:
		contents = yaml.load(fn)
	return contents


def run_cmd(command):
	stdout = None
	stderr = None
	process = Popen(command, shell=False, stdout=PIPE, stderr=PIPE)
	stdout, stderr = process.communicate()
	output = stdout + stderr
	returncode = process.returncode
	return output, returncode


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
	return '%s/%s/%s' %(PATH[kind], bundle['name'], bundle['version'])


def get_bundle_code(bundle):
	errcode = None
	folder = get_bundle_path(bundle)
	
	scm = {
		'git'	: Git,
	}
	code = scm[bundle['scm']](bundle['src'], folder)
	print 'Getting %s from %s (%s)...' %(bundle['name'], bundle['src'], bundle['version']) ,
	ok = code.get(bundle['version'])
	if ok:
		msg = bcolors.OKGREEN + 'OK' + bcolors.ENDC
	else:
		msg = bcolors.FAIL + 'ERROR' + bcolors.ENDC
	print msg
	return ok


def get_dependencies_tree(root):
	deps = list()
	for (dir, _, filenames) in os.walk(PATH[root]):
		for filename in filenames:
			path = os.path.join(dir, filename)
			if 'meta/main.yml' in path:
				deps += get_all_bundles_in_yml(load_yml(path))

	pendant = list()
	for bundle in deps:
		if not os.path.exists(get_bundle_path(bundle)):
			pendant.append(bundle)

	retval = list()
	repeated = list()
	for bundle in pendant:
		src = bundle.get('src')
		if src not in repeated:
			retval.append(bundle)
			repeated.append(src)
	return retval


def main():
	downloaded = list()

	## Get bundles from specific YML file
	filename = sys.argv[1] if len(sys.argv)>1 else 'site.yml'
	if os.path.exists(filename):
		for bundle in get_all_bundles_in_yml(load_yml(filename)):
			if not os.path.exists(get_bundle_path(bundle)):
				downloaded.append(bundle)
				get_bundle_code (bundle)


	## Get bundles from dependecies for each meta/main.yml in every bundle
	waitlist = ['dummy']
	while len(waitlist)>0:
		dependencies = get_dependencies_tree('role') + get_dependencies_tree('library')
		waitlist = [item for item in dependencies if item not in downloaded]
		for bundle in waitlist:
			downloaded.append(bundle)
			get_bundle_code (bundle)

	if len(errorlist)>0:
		print '\nErrors found:'
		for msg in errorlist: print msg

########################################################
errorlist = list()
main()
