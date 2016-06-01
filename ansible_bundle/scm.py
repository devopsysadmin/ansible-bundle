#!/usr/bin/env python2
# -*- encoding: utf8 -*-

import defaults
import shell


class Git:
    url = None
    path = None
    branch = None

    def __init__(self, url, path='.', branch='master'):
        self.url = url
        self.path = path
        self.branch = branch

    def get(self):
        cmd = ['git', 'clone', '--branch', self.branch,
               '--depth', '1', self.url, self.path]
        stdout, rc = shell.run(cmd)
        if rc == shell.OK:
            return True
        else:
            return False

    def update(self):
        shell.cd(self.path)
        cmd = ['git', 'fetch', 'origin', self.branch]
        stdout, rc = shell.run(cmd)
        shell.cd(shell.WORKDIR)
        if rc == shell.OK:
            return True
        else:
            return False
