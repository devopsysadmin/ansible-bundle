#!/usr/bin/env python2
# -*- encoding: utf8 -*-
#

import argparse
import shell
from bundle import Bundle, PATH

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', dest='filename', default='site.yml',
        help='YML file to be processed (default:site.yml)')
    parser.add_argument('--run', action='store_true', dest='run_playbook',
        default=False, 
        help='Runs ansible-playbook with default params after getting bundles')
    parser.add_argument('--args', dest='args', nargs='?',
        help='ansible-playbook arguments, if needed. Must be put into quotes')

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
            yml+=(shell.load(include))
        else:
            yml+=append(element)
    return yml

def main():
    params = get_arguments()
    downloaded=list()

    ## End if file doesn't exist
    if not shell.isfile(params.filename):
        raise Exception('File %s not found' %params.filename)

    ## Get contents and includes from main YML
    yml = expand(shell.load(params.filename))

    ## Get bundles from main yml and its includes
    bundles = list()
    for item in yml:
        bundles += get_bundles_from(item)

    while len(bundles)>0:
        for bundle in bundles:
            bundles.remove(bundle)
            if bundle.download() is True:
                downloaded.append(bundle.name)
            else:
                return shell.ERROR
        dependencies = get_dependencies_tree(PATH['role']) + get_dependencies_tree(PATH['library'])
        bundles = [item for item in bundles if item.name not in downloaded] + [ item for item in dependencies if item.name not in downloaded ]

    ## After getting bundles, run playbook if set to
    if params.run_playbook is True:
        args = params.args.split() if params.args else list()
        ansiblecmd = ['ansible-playbook', params.filename ] + args

        shell.echo('Running', typeOf='info', lr=False)
        shell.echo(shell.Color.text(' '.join(ansiblecmd), decoration='bold'))
        shell.call(ansiblecmd)


 ########################################################
if __name__ == "__main__":
    shell.exit(main())
