# -*- encoding: utf8 -*-
#

import argparse
import shlex
from ansible_bundle import shell, defaults, worker
from ansible_bundle.bundle import Bundle
import time

DEFAULT_VERBOSITY=defaults.QUIET
DEFAULT_DRY=defaults.DRY
DEFAULT_CLEAN=defaults.CLEAN
DEFAULT_RUN=defaults.RUN

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='YML file to be processed')
    parser.add_argument('--bundle-clean-roles', dest='clean', action='store_true', default=DEFAULT_CLEAN,
                        help='clean roles and libraries directories')
    parser.add_argument('--bundle-dry', dest='dry', action='store_true', default=DEFAULT_DRY,
                        help='Will give info about the changes to be performed')
    parser.add_argument('--bundle-deps-only', dest='dont_play', action='store_true', default=False,
                        help='Don\'t run the playbook after getting dependencies')
    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('--version', action='version', version='%s %s' %(shell.prog, shell.version) )
    parser.add_argument('--bundle-disable-color', dest='use_colors', action='store_false', default=True,
                        help='Don\'t colorize console output')
    parser.add_argument('--bundle-workers', dest='workers', type=int,
                        help='Concurrent downloads when getting roles. Default: %s' %defaults.Config.workers)
    parser.add_argument('--bundle-safe-update', dest='safe', action='store_true', default=False,
                        help='If role directory exists, don\'t perform any change')
    return parser.parse_known_args()


def clean_roles():
    shell.echo_info('Cleaning roles directory...')
    shell.rmdir('roles')


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

def main():
    args, ansible = get_arguments()

    ## If debug mode is enabled, reduce workers to 1 for better printing
    if args.verbose > 2: args.workers=1

    shell.config.initialize(
        verbosity=args.verbose,
        workers=args.workers,
        safe=args.safe
        )
    shell.config.dry = args.dry
    shell.config.colorize = args.use_colors
    pool = shell.config.pool

    if args.clean is True:
        clean_roles()

    yml = load_site(args.filename)
    downloaded = ['dummy']

    ## Download roles and dependencies in threaded workers. Then wait for them to be finished
    for task in [ item for sublist in [ item.get('roles') for item in yml if item.get('roles') ] for item in sublist ]:
        role = Bundle.from_dict(task)
        pool.add_task(role.download, downloaded)
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
