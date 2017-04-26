#!/usr/bin/env python3
# -*- encoding: utf8 -*-
#

from ansible_bundle import shell
from ansible_bundle.scm import Git

WORKDIR = shell.WORKDIR


class Role(object):
    name = None
    path = None
    version = None
    url = None

    def __init__(self, raw):
        if isinstance(raw, dict):
            split = raw.get('role', 'unnamed').split('@')
        else:
            split = raw.split('@')

        if isinstance(raw, dict):
            _split = raw.get('role', 'unnamed').split('/')
        else:
            _split = raw.split('/')

        if len(_split)>len(split):
            split = _split
            shell.echo_warning('Deprecation warning: plese use {name}@{version} instead of {name}/{version}'.format(
                name=split[0],
                version=split[1])
            )
            separator = '/'
        else:
            separator = '@'

        self.name = split[0]
        self.url = '%s/%s' % (shell.config.url, self.name)

        if len(split)>1:
            self.version = split[1]
            self.path = shell.path(WORKDIR, 'roles', '%s%s%s' %(self.name, separator, self.version))
        else:
            self.version = 'master'
            self.path = shell.path(WORKDIR, 'roles', self.name)

class Bundle(object):

    name = None
    path = None
    version = None
    url = None
    exists = False
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
            contents = shell.load(meta)
            if contents is None:
                contents = dict()
            for dep in contents.get('dependencies', list()):
                deps.append(Bundle.from_dict(dep))
        return deps

    def __init__(self, typeof, raw):
        bundle = Role(raw)
        for key in ('name', 'path', 'version', 'url'):
            setattr(self, key, getattr(bundle, key))
        if shell.isdir(self.path):
            self.exists = True
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

    def download(self, check_array=None):
        git = Git(
            self.url,
            self.path,
            self.version,
            self.name,
            shell.config.safe
        )
        func = git.update if self.exists else git.get
        if check_array and self.properties not in check_array:
            check_array.append(self.properties)
            if func():
                for dependency in self.dependencies():
                    dependency.download(check_array)
