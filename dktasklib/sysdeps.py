# -*- coding: utf-8 -*-
import sys
from dkfileutils.which import get_executable
from invoke import run, ctask as task


@task
def have_nodejs(ctx):
    if sys.platform == 'win32':  # pragma: nocover
        nodeexe = get_executable('node')
    else:  # pragma: nocover
        nodeexe = get_executable('nodejs') or get_executable('node')

    if not nodeexe:  # pragma: nocover
        print """
        Install Node.js using your OS package manager
        https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager
        """
        return None
    ctx.nodejs = nodeexe
    return nodeexe


@task
def have_xnpm(ctx):
    print "CONFIG:", ctx.config.keys()
    npm_exe = get_executable('xnpm')
    if not npm_exe:  # pragma: nocover
        print """
        Install Node.js using your OS package manager
        https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager
        """
        return None
    # ctx['npm'] = npm_exe
    ctx.npm = npm_exe
    return npm_exe


@task
def have_npm(ctx):
    npm_exe = get_executable('npm')
    if not npm_exe:  # pragma: nocover
        print """
        Install Node.js using your OS package manager
        https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager
        """
        return None
    # ctx['npm'] = npm_exe
    ctx.npm = npm_exe
    print "CONFIG:", ctx.config.keys()
    return npm_exe


@task(have_nodejs, have_npm)
def have_lessc(ctx):
    lessc = get_executable('lessc')
    if not lessc:  # pragma: nocover
        print """
        Install less.js by issuing:  npm install -g less
        """
        return None
    ctx.lessc = lessc
    return lessc
