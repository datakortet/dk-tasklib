# -*- coding: utf-8 -*-

"""Commands installed by setup.py
"""
# pragma: nocover
import argparse
import os
import sys

import shutil
from dkfileutils.path import Path
from .._version import __version__

DIRNAME = Path(os.path.dirname(__file__))


def install_cmd(args):
    """Install a basic task.py to the current directory.
    """
    cwd = Path.curdir()
    tasks_file = cwd / 'tasks.py'
    if tasks_file.exists() and not args.force:
        print "tasks.py exists (use --force to overwrite)"
        sys.exit(1)
    shutil.copyfile(
        DIRNAME / 'taskbase.py',
        cwd / 'tasks.py'
    )


def main(args=None):
    args = args or sys.argv[1:]
    p = argparse.ArgumentParser()
    commands = list(sorted([name[:-4] for name in globals()
                            if name.endswith('_cmd')]))

    p.add_argument(
        'command',
        help="run command (available commands: %s)" % ', '.join(commands)
    )
    p.add_argument(
        '--force', '-f', action='store_true',
        help="force execution of commands."
    )
    p.add_argument(
        '--verbose', '-v', action='store_true',
        help="verbose output"
    )
    p.add_argument(
        '--version', action='version',
        version='%(prog)s ' + __version__
    )

    # print "ARGS1:", args
    args = p.parse_args(args)
    # print "ARGS2:", args

    if args.verbose:
        print "ARGS:", args

    if args.command not in commands:
        print "Unknown command:", args.command
        sys.exit(1)

    globals()[args.command + '_cmd'](args)


if __name__ == "__main__":
    main()
