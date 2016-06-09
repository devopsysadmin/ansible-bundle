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

    def _is_branch(self):
        with open(shell.path('.git', 'HEAD')) as fn:
            ref = fn.read()
        return self.branch in ref

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
        if self._is_branch():
            cmds = (
                ['git', 'checkout', '.'],
                ['git', 'pull', '--rebase', 'origin', self.branch],
                )
            for cmd in cmds:
                stdout, rc = shell.run(cmd)
                if rc == shell.ERROR:
                    return False
            shell.cd(shell.WORKDIR)
        elif shell.config.verbose > defaults.QUIET:
            shell.echo_info('Current branch is really a tag. Skip.\n')
        return True