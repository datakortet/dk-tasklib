# -*- coding: utf-8 -*-
"""
Base version of package/tasks.py.

Copy this file to your package and modify it.
"""
# pragma: nocover
import os

from invoke import ctask as task, collection
from dktasklib.package import Package
from dkfileutils.path import Path
from dkfileutils.changed import changed
from dktasklib.manage import collectstatic
from dktasklib import lessc
from dktasklib import docs as doctools
from dktasklib import jstools
from dktasklib import version, upversion
from dktasklib.watch import Watcher

DIRNAME = Path(os.path.dirname(__file__))

# collectstatic
# --------------
# Specify which settings file should be used when running
# `python manage.py collectstatic` (must be on the path or package root
# directory).
DJANGO_SETTINGS_MODULE = ''

# .less
# ------
# there should be a mypkg/mypkg/less/mypkg.less file that imports any other
# needed sources

# .jsx (es6 source)
# ------------------
# list any .jsx files here. Only filename.jsx (don't include the path).
# The files should reside in mypkg/mypkg/js/ directory.
JSX_FILENAMES = []


@task
def build_js(ctx, force=False):
    """Build all javascript files.
    """
    for fname in JSX_FILENAMES:
        jstools.babel(
            ctx,
            '{pkg.sourcedir}/js/' + fname,
            '{pkg.staticdir}/{pkg.name}/js/' + fname + '.js',
            force=force
        )


@task
def build(ctx, less=False, docs=False, js=False, force=False):
    """Build everything and collectstatic.
    """
    specified = any([less, docs, js])
    buildall = not specified

    if buildall or less:
        less_fname = ctx.pkg.sourcedir / 'less' / ctx.pkg.name + '.less'
        if less_fname.exists():
            lessc.LessRule(
                ctx,
                src='{pkg.sourcedir}/less/{pkg.name}.less',
                dst='{pkg.staticdir}/{pkg.name}/css/{pkg.name}-{version}.min.css',
                force=force
            )
        elif less:
            print "WARNING: build --less specified, but no file at:", less_fname

    if buildall or docs:
        doctools.build(ctx, force=force)

    if buildall or js:
        build_js(ctx, force)

    if DJANGO_SETTINGS_MODULE and (force or changed(ctx.pkg.staticdir)):
        collectstatic(ctx, DJANGO_SETTINGS_MODULE)


@task
def watch(ctx):
    """Automatically run build whenever a relevant file changes.
    """
    watcher = Watcher(ctx)
    watcher.watch_directory(
        path='{pkg.sourcedir}/less', ext='.less',
        action=lambda e: build(ctx, less=True)
    )
    watcher.watch_directory(
        path='{pkg.sourcedir}/js', ext='.jsx',
        action=lambda e: build(ctx, js=True)
    )
    watcher.watch_directory(
        path='{pkg.docsdir}', ext='.rst',
        action=lambda e: build(ctx, docs=True)
    )
    watcher.start()


# individual tasks that can be run from this project
ns = collection.Collection(
    build,
    watch,
    build_js,
    lessc,
    doctools,
    version, upversion,
    collectstatic,
)
ns.configure({
    'pkg': Package()
})
