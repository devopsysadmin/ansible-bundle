#!/usr/bin/env python2
# -*- encoding: utf8 -*-

import shell


class Git:
    url = None
    path = None
    branch = None
    verbose = False

    def __init__(self, url, path='.', branch='master', verbose=0):
        self.url = url
        self.path = path
        self.branch = branch
        self.verbose = verbose

    def get(self):
        cmd = ['git', 'clone', '--branch', self.branch,
               '--depth', '1', self.url, self.path]
        stdout, rc = shell.run(cmd, verbose=self.verbose)
        if rc == shell.OK:
            return True
        else:
            return False

    def update(self):
        shell.cd(self.path)
        cmd = ['git', 'pull', 'origin', self.branch]
        stdout, rc = shell.run(cmd, verbose=self.verbose)
        shell.cd(shell.WORKDIR)
        if rc == shell.OK:
            return True
        else:
            return False
