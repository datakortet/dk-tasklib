import os
import webbrowser
from os.path import join
import sys

from invoke import ctask as task, Collection
from .utils import cd


# Underscored func name to avoid shadowing kwargs in build()
@task(name='clean')
def _clean(ctx):
    """Nuke docs build target directory so next build is clean.
    """
    builddir = ctx.docs.builddir
    if os.path.exists(builddir) and len(os.listdir(builddir)) > 0:
        ctx.run("rm -rf {0}/*".format(builddir))


# Ditto
@task(name='browse')
def _browse(ctx):
    """Open build target's index.html in a browser (using 'open').
    """
    index = join(ctx.docs.builddir, ctx.docs.target_file)
    webbrowser.open_new(index)


# @task
# def build(ctx):
#     "Build sphinx docs."
#     sphinxdir = os.path.join(os.environ['DKROOT'], 'sphinxdoc')   # XXX
#     with cd('docs'):
#         ctx.run("sphinx-build -a -E -T -c {sphinxdir} -b html . ./html".format(**locals()))


@task(default=True, help={
    'opts': "Extra sphinx-build options/args",
    'clean': "Remove build tree before building",
    'browse': "Open docs index in browser after building",
    'warn': "Build with stricter warnings/errors enabled",
})
def build(ctx, clean=False, browse=False, warn=False, opts=""):
    """
    Build the project's Sphinx docs.
    """

    x = """
    ::

        Usage: inv[oke] [--core-opts] docs [--options] [other tasks here ...]

        Docstring:
          Build the project's Sphinx docs.

        Options:
          -b, --browse               Open docs index in browser after building
          -c, --clean                Remove build tree before building
          -o STRING, --opts=STRING   Extra sphinx-build options/args
          -w, --warn                 Build with stricter warnings/errors enabled

    """
    if clean:
        _clean(ctx)
    if opts is None:
        opts = ""
    if warn:
        opts += " -n -W"
    cmd = "sphinx-build {opts} {ctx.docs.source} {ctx.docs.builddir}".format(
        opts=opts, ctx=ctx)
    ctx.run(cmd)
    if browse:
        _browse(ctx)


@task
def tree(ctx):
    """Display the docs tree.
    """
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    ctx.run('tree -Ca -I "{0}" {1}'.format(ignore, ctx.docs.source))


# Vanilla/default/parameterized collection for normal use
docs = Collection('docs', _clean, _browse, build, tree)
docs.configure({
    'docs': {
        'source': 'docs',
        'builddir': join('build', 'docs'),
        'target_file': 'index.html',
    }
})
