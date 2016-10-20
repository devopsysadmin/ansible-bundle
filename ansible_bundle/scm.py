# -*- encoding: utf8 -*-

from ansible_bundle import shell, defaults

class Git:
    url = None
    path = None
    branch = None
    name = None

    def __init__(self, url, path='.', branch='master', name=None):
        self.url = url
        self.path = path
        self.branch = branch
        self.name = name

    def _is_branch(self):
        with open(shell.path('.git', 'HEAD')) as fn:
            ref = fn.read()
        return self.branch in ref

    def get(self):
        shell.echo_info('Getting %s (%s) ...' %(self.name, self.branch))
        cmd = ['git', 'clone', '--branch', self.branch,
               '--depth', '1', self.url, self.path]
        rc, stdout = shell.run(cmd)
        shell.cd(shell.WORKDIR)
        if rc == shell.OK:
            return True
        else:
            return False

    def update(self):
        shell.echo_info('Updating %s (%s) ...' %(self.name, self.branch))
        shell.cd(self.path)
        if self._is_branch():
            cmds = (
                ['git', 'checkout', '.'],
                ['git', 'pull', '--rebase', 'origin', self.branch],
                )
            for cmd in cmds:
                rc, stdout = shell.run(cmd)
                if rc == shell.ERROR:
                    return False
        shell.cd(shell.WORKDIR)
        return True