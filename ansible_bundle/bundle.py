#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import shell
from scm import Git

WORKDIR = shell.WORKDIR
DEFAULTS = shell.DEFAULTS

PATH = {
    'role': 'roles/',
    'library': 'modules/'
}


class Bundle(object):

    name = None
    path = None
    version = None
    url = None

    def __init__(self, typeof, raw):
        if typeof == 'role':
            self.__role(raw)

    def __str__(self):
        string = """
            name    : %s
            path    : %s
            version : %s
            url     : %s
        """.replace('\t', '') % (
            self.name,
            self.path,
            self.version,
            self.url
        )
        return string

    def __role(self, raw):
        self.name, self.version = self.__generate_name_version(raw)
        self.path = self.__generate_path(self.name, self.version)
        self.url = self.__generate_url(self.name)

    def __generate_url(self, name):
        return '%s/%s' % (DEFAULTS.SCM_ROLES, name)

    def __generate_name_version(self, raw):
        if isinstance(raw, dict):
            split = raw.get('role', 'unnamed').split('/')
        else:
            split = raw.split('/')
        name = split[0]
        version = split[1] if len(split) > 1 else DEFAULTS.SCM_VERSION
        return name, version

    def __generate_path(self, name, version):
        path = shell.path(WORKDIR, PATH['role'], name)
        if version != 'master':
            path = shell.path(path, version)
        return path

    def download(self):
        git = Git(self.url, self.path, self.version)
        if shell.isdir(self.path):
            msg = 'Updating'
            func = git.update
        else:
            msg = 'Getting'
            func = git.get
        shell.echo('%s %s from %s (%s)...' % (msg, self.name,
                                              self.url, self.version),
                   typeOf='info', lr=False)
        ok = func()
        if ok:
            shell.echo('OK', typeOf='ok')
        else:
            shell.echo('ERROR', typeOf='error')
        return ok
