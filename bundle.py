#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import shell
from scm import Git

WORKDIR = shell.WORKDIR
DEFAULTS = shell.DEFAULTS

PATH = {
    'role' : 'roles/',
    'library' : 'modules/'
}

class Bundle(object):

    name = None

    def __init__(self, typeof, raw):
        if typeof == 'role':
            self.__role(raw)

    def __str__(self):
        string = """
            name : %s
            path : %s
            version : %s
            url: %s
        """.replace('\t', '') %(
            self.name,
            self.path,
            self.version,
            self.url
            )
        return string

    def __get_name_version(self, string):
        split = string.split('/')
        name = split[0]
        version = split[1] if len(split)>1 else DEFAULTS.SCM_VERSION
        return name, version

    def __role(self, raw):
        self.name, self.version = self.__get_name_version(raw.get('role', 'unnamed'))
        self.path = shell.path(WORKDIR, PATH['role'], self.name)
        self.url = '%s/%s' %(DEFAULTS.SCM_ROLES, self.name)


    def download(self):
        git = Git(self.url, self.path)
        if shell.isdir(self.path):
            msg = 'Updating'
            func = git.update
            args = None
        else:
            msg = 'Getting'
            func = git.get
            args = self.version
        shell.echo('%s %s from %s (%s)...' %(msg, self.name, self.url, self.version), typeOf='info', lr=False)
        ok = func(args) if args else func()
        if ok:
            shell.echo('OK', typeOf='ok')
        else:
            shell.echo('ERROR', typeOf='error')
        return ok
