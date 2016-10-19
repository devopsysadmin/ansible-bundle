# -*- encoding: utf8 -*-
#

import argparse
import shlex
from ansible_bundle import shell, defaults, worker
from ansible_bundle.bundle import Bundle, PATH
import time

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
    parser.add_argument('--bundle-workers', dest='workers', type=int, default=0,
                        help='Concurrent downloads when getting roles. Default: %s' %defaults.Config.workers)
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

def download(pool, bundle):
    if bundle.properties not in downloaded:
        downloaded.append(bundle.properties)
        action = 'Updating' if bundle.exists else 'Getting'
        shell.echo_info('%s %s (%s)...' %(action, bundle.name, bundle.version), lr=True)
        pool.add_task(bundle.download)
    for dep in bundle.dependencies():
        download(pool, dep)

def items(bundle, yml):
    return [ item for sublist in [ item.get(bundle) for item in yml if item.get(bundle) ] for item in sublist ]

def main():
    args, ansible = get_arguments()
    shell.config.initialize()
    shell.config.verbose = args.verbose
    shell.config.dry = args.dry
    shell.config.colorize = args.use_colors
    if args.workers > 0: shell.config.workers = args.workers

    if args.clean is True:
        clean_dirs(['roles'])

    yml = load_site(args.filename)
    tasks = items('roles', yml) + items('libraries', yml)
    
    pool = worker.ThreadPool(shell.config.workers)
    for task in tasks:
        download(pool, Bundle.from_dict(task))
    pool.wait_completion()

    # After getting bundles, run playbook if set to
    if args.dry is True:
        shell.echo_warning('--dry was set. End.')
    elif args.dont_play is True:
        shell.echo_warning('--bundle-deps-only was set. Exit.')
    else:
        shell.echo('\nRunning playbook', color='yellow')
        run_playbook(args.filename, ansible, args.verbose)

########################################################
if __name__ == "__main__":
    shell.exit(main())
