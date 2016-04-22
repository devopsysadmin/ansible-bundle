#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import shell

class Git:
	url = None
	path = None
	tag = None

	def __init__(self, url, path):
		self.url = url
		self.path = path

	def get(self, version):
		cmd = [ 'git','clone', '--branch', version, '--depth', '1', self.url, self.path ]
		stdout, rc = shell.run(cmd)
		if rc == shell.OK :
			return True
		else:
			return False

	def branch(self):
		cmd = ['git', 'branch']
		stdout, rc = shell.run(cmd)
		if rc == shell.OK:
			return stdout.split(' ')[1].replace('\n', '')
		else:
			raise Exception('Could not get current branch')

	def update(self):
		shell.cd(self.path)
		cmd = ['git', 'pull', 'origin', self.branch() ]
		stdout, rc = shell.run(cmd)
		shell.cd(shell.WORKDIR)
		if rc == shell.OK:
			return True
		else:
			return False
