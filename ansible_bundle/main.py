# -*- encoding: utf8 -*-
#

import argparse
import shlex
from ansible_bundle import shell, defaults
from ansible_bundle.bundle import Bundle, PATH

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
    parser.add_argument('--bundle-deps-only', dest='dont_play', action='store_true', default=False,
                        help='Don\'t run the playbook after getting dependencies')
    parser.add_argument('-v', '--verbose', action='count', default=DEFAULT_VERBOSITY)
    parser.add_argument('--version', action='version', version='%s %s' %(shell.prog, shell.version) )
    parser.add_argument('--bundle-disable-color', dest='use_colors', action='store_false', default=True,
                        help='Don\'t colorize console output')
    parser.add_argument('--bundle-workers', dest='jobs', type=int, default=1,
                        help='Concurrent downloads when getting roles')
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
        rc = shell.call(cmd)
    except KeyboardInterrupt:
        rc = 1
    shell.exit(rc)


def download(bundle):
    if bundle.properties not in downloaded:
        bundle.download()
        downloaded.append(bundle.properties)
        for dep in bundle.dependencies():
            download(dep)

def items(bundle, yml):
    return [ item for sublist in [ item.get(bundle) for item in yml if item.get(bundle) ] for item in sublist ]

def main():
    args, ansible = get_arguments()
    shell.config.initialize()
    shell.config.verbose = args.verbose
    shell.config.dry = args.dry
    shell.config.colorize = args.use_colors

    if args.clean is True:
        clean_dirs(['roles'])

    yml = load_site(args.filename)
    tasks = items('roles', yml) + items('libraries', yml)

    for task in tasks:
        download(Bundle.from_dict(task))

    # After getting bundles, run playbook if set to
    if args.dry is True:
        shell.echo_warning('--dry was set. End.')
    elif args.dont_play is True:
        shell.echo_warning('--bundle-deps-only was set. Exit.')
    else:
        run_playbook(args.filename, ansible, args.verbose)

########################################################
if __name__ == "__main__":
    shell.exit(main())
