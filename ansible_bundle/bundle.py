#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import defaults
import shell
from scm import Git

WORKDIR = shell.WORKDIR
CONFIG = shell.config

PATH = {
    'role': 'roles/',
    'library': 'modules/',
}


class Role(object):
    name = None
    path = None
    version = None
    url = None

    def __init__(self, raw):
        self.name, self.version = self.generate_name_version(raw)
        self.path = self.generate_path(self.name, self.version)
        self.url = self.generate_url(self.name)

    def generate_name_version(self, raw):
        if isinstance(raw, dict):
            split = raw.get('role', 'unnamed').split('/')
        else:
            split = raw.split('/')
        name = split[0]
        version = split[1] if len(split) > 1 else CONFIG.SCM_VERSION
        return name, version

    def generate_url(self, name):
        return '%s/%s' % (CONFIG.SCM_ROLES, name)

    def generate_path(self, name, version):
        if version == CONFIG.SCM_VERSION:
            return shell.path(WORKDIR, PATH['role'], 'unversioned', name)
        else:
            return shell.path(WORKDIR, PATH['role'], name, version)


class Bundle(object):

    name = None
    path = None
    version = None
    url = None
    properties = (name, version)

    @classmethod
    def from_dict(bundle, json):
        if isinstance(json, dict):
            if json.get('role', None):
                return bundle('role', json)
        else:
            return bundle('role', json)

    def dependencies(self):
        deps = list()
        meta = shell.path(self.path, 'meta', 'main.yml')
        if shell.isfile(meta):
            for dep in shell.load(meta).get('dependencies'):
                deps.append(Bundle.from_dict(dep))
        return deps

    def __init__(self, typeof, raw):
        if typeof == 'role':
            bundle = Role(raw)
        for key in ('name', 'path', 'version', 'url'):
            setattr(self, key, getattr(bundle, key))
        self.__update_properties()

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

    def __update_properties(self):
        self.properties = (self.name, self.version)

    def download(self):
        git = Git(self.url, self.path, self.version)
        if shell.isdir(self.path):
            msg = 'Updating'
            func = git.update
        else:
            msg = 'Getting'
            func = git.get
        if shell.config.verbose < defaults.DEBUG:
            shell.echo_info ('%s %s (%s)...' %
                                (msg, self.name, self.version),
                            lr=False
                            )
        ok = func()
        if shell.config.verbose < defaults.DEBUG:
            if ok:
                shell.echo('OK', typeOf='ok')
            else:
                shell.echo('ERROR', typeOf='error')
        return ok
