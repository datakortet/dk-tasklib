import os
from os.path import join
import sys

from invoke import ctask as task, Collection
from .utils import cd


# Underscored func name to avoid shadowing kwargs in build()
@task(name='clean')
def _clean(c):
    """
    Nuke docs build target directory so next build is clean.
    """
    c.run("rm -rf {0}".format(c.sphinx.target))


# Ditto
@task(name='browse')
def _browse(c):
    """
    Open build target's index.html in a browser (using 'open').
    """
    index = join(c.sphinx.target, c.sphinx.target_file)
    c.run("open {0}".format(index))


@task
def build(ctx):
    "Build sphinx docs."
    sphinxdir = os.path.join(os.environ['DKROOT'], 'sphinxdoc')   # XXX
    with cd('docs'):
        ctx.run("sphinx-build -a -E -T -c {sphinxdir} -b html . ./html".format(**locals()))


# @task(default=True, help={
#     'opts': "Extra sphinx-build options/args",
#     'clean': "Remove build tree before building",
#     'browse': "Open docs index in browser after building",
#     'warn': "Build with stricter warnings/errors enabled",
# })
# def build(c, clean=False, browse=False, warn=False, opts=None):
#     """
#     Build the project's Sphinx docs.
#     """
#     if clean:
#         _clean(c)
#     if opts is None:
#         opts = ""
#     if warn:
#         opts += " -n -W"
#     cmd = "sphinx-build{2} {0} {1}".format(
#         c.sphinx.source,
#         c.sphinx.target,
#         (" " + opts) if opts else "",
#     )
#     c.run(cmd)
#     if browse:
#         _browse(c)


@task
def tree(c):
    "Display the docs tree."
    ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"
    c.run("tree -Ca -I \"{0}\" {1}".format(ignore, c.sphinx.source))


# Vanilla/default/parameterized collection for normal use
docs = Collection('docs', _clean, _browse, build, tree)
docs.configure({
    'sphinx': {
        'source': 'docs',
        # TODO: allow lazy eval so one attr can refer to another?
        'target': join('docs', '_build'),
        'target_file': 'index.html',
    }
})
