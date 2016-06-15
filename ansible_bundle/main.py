#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import argparse
import shell
import defaults
from bundle import Bundle, PATH
import shlex

DEFAULT_VERBOSITY=defaults.QUIET
DEFAULT_DRY=defaults.DRY
DEFAULT_CLEAN=defaults.CLEAN
DEFAULT_RUN=defaults.RUN

downloaded = list()


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='filename', default='site.yml',
                        help='YML file to be processed (default:site.yml)')
    parser.add_argument('--run', action='store_true', dest='run_playbook',
                        default=DEFAULT_RUN,
                        help='Runs ansible-playbook with default params' +
                        ' after getting bundles')
    parser.add_argument('--args', dest='args', nargs='?',
                        help='ansible-playbook arguments, if needed. Must be' +
                        ' put into quotes')
    parser.add_argument('--clean', action='store_true', default=DEFAULT_CLEAN,
                        help='clean roles and libraries directories')
    parser.add_argument('-v', '--verbose', action='count', default=DEFAULT_VERBOSITY,
                        help='Be verbose on tasks')
    parser.add_argument('--dry', action='store_true', default=DEFAULT_DRY,
                        help='Will give info about the changes to be performed')

    return parser.parse_args()


def run_playbook(filename, args):
        ## str.split() splits even doble quotes. Shlex.split() surpasses them
        args_array = shlex.split(args)
        print('')
        ansiblecmd = ['ansible-playbook' ] + args_array + [ filename ]
        shell.echo('Running ', typeOf='info', lr=False)
        shell.echo(shell.Color.text(' '.join(ansiblecmd), decoration='bold'))
        shell.call(ansiblecmd)


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

def download(bundle):
    if bundle.properties not in downloaded:
        bundle.download()
        downloaded.append(bundle.properties)
        for dep in bundle.dependencies():
            download(dep)

def items(bundle, yml):
    return [ item for sublist in [ item.get(bundle) for item in yml if item.get(bundle) ] for item in sublist ]

def main():
    params = get_arguments()

    shell.config.verbose = params.verbose
    shell.config.dry = params.dry

    if params.clean is True:
        clean_dirs(['roles'])

    yml = load_site(params.filename)
    tasks = items('roles', yml) + items('libraries', yml)

    for task in tasks:
        download(Bundle.from_dict(task))

    # After getting bundles, run playbook if set to
    if params.run_playbook is True:
        if params.dry is True:
            shell.echo_warning('--run passed and --dry set to true. End.')
        else:
            run_playbook(params.filename, params.args)

########################################################
if __name__ == "__main__":
    shell.exit(main())
