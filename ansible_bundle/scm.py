# -*- encoding: utf8 -*-

from ansible_bundle import shell, defaults

class Git:
    url = None
    path = None
    branch = None
    name = None
    safe = False

    def __init__(self, url, path='.', branch='master', name=None, safe=False):
        self.url = url
        self.path = path
        self.branch = branch
        self.name = name
        self.safe = safe

    def _is_branch(self):
        with open(shell.path(self.path, '.git', 'HEAD')) as fn:
            ref = fn.read()
        return self.branch in ref

    def get(self):
        shell.echo_info('Getting %s (%s) ...' %(self.name, self.branch))
        cmd = ['git', 'clone', '--branch', self.branch,
               '--depth', '1', self.url, self.path]
        rc, stdout = shell.run(cmd)
        if rc == shell.OK:
            return True
        else:
            return False

    def update(self):
        shell.echo_info('Updating %s (%s) ...' %(self.name, self.branch))
        is_branch = self._is_branch()
        clean = ['git', '-C', self.path, 'reset', '--hard']
        update = ['git', '-C', self.path, 'pull', '--rebase', 'origin', self.branch]
        if is_branch and not self.safe:
            for cmd in (clean, update):
                rc, stdout = shell.run(cmd)
                if rc == shell.ERROR:
                    return False
        elif is_branch and self.safe:
            shell.echo_debug('As bundle-safe-update was set, directory will not change')
        elif not is_branch:
            shell.echo_debug('Current branch mismatches bundle version. Assuming tag and skip.')
        return True