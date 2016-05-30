#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import argparse
import shell
from bundle import Bundle, PATH


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='filename', default='site.yml',
                        help='YML file to be processed (default:site.yml)')
    parser.add_argument('--run', action='store_true', dest='run_playbook',
                        default=False,
                        help='Runs ansible-playbook with default params' +
                        ' after getting bundles')
    parser.add_argument('--args', dest='args', nargs='?',
                        help='ansible-playbook arguments, if needed. Must be' +
                        ' put into quotes')
    parser.add_argument('--clean', action='store_true', default=False,
                        help='clean roles and libraries directories')

    return parser.parse_args()


def get_dependencies_tree(pathDir):
    deps = list()
    for (directory, _, filenames) in shell.walk(pathDir):
        for filename in filenames:
            path = shell.path(directory, filename)
            if 'meta/main.yml' in path:
                deps += get_bundles_from(shell.load(path))
    return list(set(deps))


def get_bundles_from(yml):
    bundles = list()
    for bundle in yml.get('roles', list()):
        b = Bundle('role', bundle)
        bundles.append(b)

    for bundle in yml.get('dependencies', list()):
        if bundle.get('role', None):
            b = Bundle('role', bundle)
            bundles.append(b)

    return list(set(bundles))


def expand(contents):
    yml = list()
    for element in contents:
        include = element.get('include', None)
        if include:
            yml += (shell.load(include))
        else:
            yml += element
    return yml


def download(filename):
    downloaded = list()

    # End if file doesn't exist
    if not shell.isfile(filename):
        raise Exception('File %s not found' % filename)

    # Get contents and includes from main YML
    yml = expand(shell.load(filename))

    # Get bundles from main yml and its includes
    bundles = list()
    for item in yml:
        bundles += get_bundles_from(item)

    while len(bundles) > 0:
        for bundle in bundles:
            bundles.remove(bundle)
            if bundle.download() is True:
                downloaded.append(bundle.name)
            else:
                return shell.ERROR
        dependencies = get_dependencies_tree(
            PATH['role']) + get_dependencies_tree(PATH['library'])
        bundles = [item for item in bundles if item.name not in downloaded] + \
            [item for item in dependencies if item.name not in downloaded]


def run_playbook(filename, args):
        ansiblecmd = ['ansible-playbook', filename] + args
        shell.echo('Running', typeOf='info', lr=False)
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



def main():
    params = get_arguments()

    if params.clean is True:
        clean_dirs(['roles'])

    download(params.filename)

    # After getting bundles, run playbook if set to
    if params.run_playbook is True:
        run_playbook(params.filename,
                     params.args.split() if params.args else list()
                    )

########################################################
if __name__ == "__main__":
    shell.exit(main())
