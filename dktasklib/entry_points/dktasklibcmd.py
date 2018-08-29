# -*- coding: utf-8 -*-

"""Commands installed by setup.py
"""
# pragma: nocover
import argparse
import os
import sys

import shutil
import textwrap

from dkfileutils.path import Path
from .._version import __version__
from .pytemplate import PyTemplate

DIRNAME = Path(os.path.dirname(__file__))


def install_cmd(args):
    """Install a basic task.py to the current directory.
    """
    cwd = Path.curdir()
    tasks_file = cwd / 'tasks.py'
    if tasks_file.exists() and not args.force:
        print "tasks.py exists (use --force to overwrite)"
        sys.exit(1)
    taskbase = DIRNAME / 'taskbase.py'
    t = PyTemplate(taskbase.read('rb'))
    tasks_file.write(t.substitute(
        VERSION=__version__
    ))
    if args.django:
        add_django_to_docs_conf()


def add_django_to_docs_conf():
    cwd = Path.curdir()
    conf_file = cwd / 'docs' / 'conf.py'
    if 'django.setup()' in conf_file.read():
        print "./docs/conf.py already contains django.setup()"
        return

    src = conf_file.read('rT')
    pre, post = src.split('\n\n', 1)
    conf_file.write(
        pre + "\n\n" +
        textwrap.dedent("""\
        import django
        django.setup()
        """) + "\n\n" +
        post
    )


def main(args=None):
    args = args or sys.argv[1:]
    p = argparse.ArgumentParser()
    commands = list(sorted([name[:-4] for name in globals()
                            if name.endswith('_cmd')]))

    p.add_argument('command', help="run command (available commands: %s)" % ', '.join(commands))
    p.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    p.add_argument('--verbose', '-v', action='store_true', help="verbose output")
    p.add_argument('--force', '-f', action='store_true', help="force execution of commands.")
    p.add_argument('--django', '-d', action='store_true', help="make django specific changes.")

    args = p.parse_args(args)

    if args.verbose:
        print "ARGS:", args

    if args.command not in commands:
        print "Unknown command:", args.command
        sys.exit(1)

    globals()[args.command + '_cmd'](args)


if __name__ == "__main__":
    main()
