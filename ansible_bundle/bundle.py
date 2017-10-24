#!/usr/bin/env python3
# -*- encoding: utf8 -*-
#

from ansible_bundle import shell
from ansible_bundle.scm import Git

WORKDIR = shell.WORKDIR

def splitted(element):
    if isinstance(element, dict):
        split = element.get('role', 'unnamed').split('@')
    else:
        split = element.split('@')

    if isinstance(element, dict):
        _split = element.get('role', 'unnamed').split('/')
    else:
        _split = element.split('/')

    if len(_split)>len(split):
        split = _split
        shell.echo_warning('Deprecation warning: plese use {name}@{version} instead of {name}/{version}'.format(
            name=split[0],
            version=split[1])
        )
        separator = '/'
    else:
        separator = '@'
    return split, separator


class Role(object):

    name = None
    path = None
    version = None
    url = None
    exists = False
    properties = (name, version)
    git_user = None
    git_pass = None

    def dependencies(self):
        deps = list()
        meta = shell.path(self.path, 'meta', 'main.yml')
        if shell.isfile(meta):
            contents = shell.load(meta)
            if contents is None:
                contents = dict()
            for role in contents.get('dependencies', list()):
                deps.append(Role(role))
        return deps

    def __init__(self, raw):
        split, separator = splitted(raw)
        self.name = split[0]
        self.url = '%s/%s' % (shell.config.url, self.name)

        if len(split)>1:
            self.version = split[1]
            self.path = shell.path(WORKDIR, 'roles', '%s%s%s' %(self.name, separator, self.version))
        else:
            self.version = 'master'
            self.path = shell.path(WORKDIR, 'roles', self.name)

        if isinstance(raw, dict):
            self.git_user = raw.get('git_user', shell.config.git_user)
            self.git_pass = raw.get('git_pass', shell.config.git_pass)

        if shell.isdir(self.path):
            self.exists = True
        self.properties = self.name, self.version

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

    def download(self, check_array=None):
        git = Git(
            url = self.url,
            path = self.path,
            version = self.version,
            name = self.name,
            safe = shell.config.safe,
            username = self.git_user,
            password = self.git_pass
        )
        func = git.update if self.exists else git.get
        if check_array and self.properties not in check_array:
            check_array.append(self.properties)
            if func():
                for dependency in self.dependencies():
                    dependency.download(check_array)
