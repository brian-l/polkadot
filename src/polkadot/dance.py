import argparse

import polkadot.loader

from polkadot.logging import logger, logging


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Load polkadot config')
    parser.add_argument(
        'config_file',
        nargs = '+',
        help = 'Required config file location.'
    )

    parser.add_argument(
        '-d', '--dry-run',
        dest = 'dry_run',
        action = 'store_true',
        default = False,
        help = 'Log the actions that would be taken instead of executing them.',
    )

    parser.add_argument(
        '-e', '--extra',
        dest = 'extras',
        action = 'append',
        default = [],
        help = 'Extra configuration options that will be passed as strings to each action.',
    )

    parser.add_argument(
        '--verbose',
        dest = 'verbose',
        action = 'store_true',
        default = False,
        help = 'Show more output than usual.',
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    cfg, = args.config_file
    dry_run = args.dry_run
    try:
        extras = dict(ext.split('=') for ext in args.extras)
    except ValueError:
        parser.error('Expected extra arguments in the form of X=Y')

    [action for action in polkadot.loader.load_config(cfg, dry_run, extras)]
