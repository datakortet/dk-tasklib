# -*- coding: utf-8 -*-

from invoke import run, ctask as task
from .sysdeps import have_xnpm


@task(have_xnpm)
def is_installed(ctx, pkgname, version=None):
    "Check if an npm package is installed."
    # rc = run('npm ls -g --depth=0 {pkgname} >NUL'.format(**locals())).return_code
    npm_exe = ctx.npm
    rc = ctx.run('"{npm_exe}" ls -g --depth=0 {pkgname} >NUL'.format(**locals())).return_code
    ctx[pkgname] = rc == 0


@task(have_xnpm)
def isinstalled(ctx, pkgname):
    "Check if an npm package is installed."
    rc = run('which {pkgname}'.format(**locals()), hide=True).return_code
    ctx[pkgname] = rc == 0


