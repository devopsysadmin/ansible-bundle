# -*- encoding: utf8 -*-

from ansible_bundle import shell, defaults

class Git:
    url = None
    path = None
    version = None
    name = None
    safe = False
    is_branch = False
    is_tag = False

    def __init__(self, url, path='.', version='master', name=None, safe=False):
        self.url = url
        self.path = path
        self.version = version
        self.name = name
        self.safe = safe
        self.is_branch, self.is_tag = self._guess_branch_or_tag()

    def _guess_branch_or_tag(self):
        head = shell.path(self.path, '.git', 'HEAD')
        with open(head, 'r') as fn:
            refs = fn.read().split('\n')[0]
        if 'refs/heads/' + self.version in refs:
            return True, False
        else:
            return False, True

    def get(self):
        shell.echo_info('Getting %s (%s) ...' %(self.name, self.version))
        cmd = ['git', 'clone', '--branch', self.version,
               '--depth', '1', self.url, self.path]
        rc, stdout = shell.run(cmd)
        if rc == shell.OK:
            return True
        else:
            return False

    def update(self):
        shell.echo_info('Updating %s (%s) ...' %(self.name, self.version))
        clean = ['git', '-C', self.path, 'reset', '--hard']
        update = ['git', '-C', self.path, 'pull', '--rebase', 'origin', self.version]
        if self.is_tag:
                shell.echo_debug('Current version is actually a tag, so no changes apply')
        elif self.is_branch and self.safe:
            shell.echo_debug('As bundle-safe-update was set, directory will not change')
        elif self.is_branch and not self.safe:
            for cmd in (clean, update):
                rc, stdout = shell.run(cmd)
                if rc == shell.ERROR:
                    return False
        else:
            shell.echo_debug('Current version mismatches bundle version. Assuming tag and skip.')
        return True