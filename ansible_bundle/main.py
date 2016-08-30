#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import argparse
import shell
import defaults
from bundle import Bundle, PATH
import shlex
import sys, os
from subprocess import call

DEFAULT_VERBOSITY=defaults.QUIET
DEFAULT_DRY=defaults.DRY
DEFAULT_CLEAN=defaults.CLEAN
DEFAULT_RUN=defaults.RUN

downloaded = list()


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='YML file to be processed')
    parser.add_argument('--bundle-clean-roles', dest='clean', action='store_true', default=DEFAULT_CLEAN,
                        help='clean roles and libraries directories')
    parser.add_argument('--bundle-dry', dest='dry', action='store_true', default=DEFAULT_DRY,
                        help='Will give info about the changes to be performed')
    parser.add_argument('-v', '--verbose', action='count')
    return parser.parse_known_args()


def clean_dirs(directories):
    for directory in directories:
        shell.echo('Cleaning %s directory...' %directory,
                   typeOf='info', lr=False)
        if shell.rmdir('roles') is True:
            shell.echo('OK', typeOf='ok')
        else:
            shell.echo('ERROR', typeOf='error')


def load_site(filename):
    if filename is None: return list()
    if not shell.isfile(filename):
        shell.echo_error('File %s not found' % filename)
        shell.exit(defaults.ERROR)
    bundlelist=list()

    ## The Playbook is always an array
    for item in shell.load(filename):
        include = item.get('include', None)
        if include:
            bundlelist += load_site(include)
        else:
            bundlelist.append(item)
    return bundlelist

def run_playbook(filename, ansible_params, verbosity=0):
    cmd = [ 'ansible-playbook', filename ] + ansible_params
    if verbosity > 0 : cmd += [ '-'+('v'*verbosity) ]
    try:
        call(cmd)
    except:
        pass

def download(bundle):
    if bundle.properties not in downloaded:
        bundle.download()
        downloaded.append(bundle.properties)
        for dep in bundle.dependencies():
            download(dep)

def items(bundle, yml):
    return [ item for sublist in [ item.get(bundle) for item in yml if item.get(bundle) ] for item in sublist ]

def main():
    params, ansible = get_arguments()

    if not params.filename:
        parser.print_help()
        print ''
        shell.echo_error('No file name specified')
        shell.exit(defaults.ERROR)

    shell.config.verbose = params.verbose
    shell.config.dry = params.dry

    if params.clean is True:
        clean_dirs(['roles'])

    yml = load_site(params.filename)
    tasks = items('roles', yml) + items('libraries', yml)

    for task in tasks:
        download(Bundle.from_dict(task))

    # After getting bundles, run playbook if set to
    if params.dry is True:
        shell.echo_warning('--dry was set. End.')
    else:
        run_playbook(params.filename, ansible, params.verbose)

########################################################
if __name__ == "__main__":
    shell.exit(main())
