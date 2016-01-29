# -*- coding: utf-8 -*-
import re
import os
import hashlib
import textwrap

from dkfileutils.path import Path
from invoke import run, ctask as task, Collection
# from .subversion import get_svn_version
from .package import Package


@task(help=dict(
    source="",
    dest_template="this filename template must contain '{version}'",
    kind="type of version number [pkg,hash]",
))
def add_version(ctx, source, dest_template, kind="pkg", force=None):
    """Add version number to a file (either pkg version, svn revision, or hash).

       Returns:
           (str) output file name
    """
    if kind == "pkg":
        ver = ctx.pkg.version
    elif kind == "hash":
        ver = hashlib.md5(open(source).read()).hexdigest()
    # elif kind == "svn":
    #     ver = get_svn_version(source)
        
    ver_fname = dest_template.format(version=ver)

    if not force and os.path.exists(ver_fname):
        if open(source).read() != open(ver_fname).read():
            print """
            There is allready a file with the current version number,
            either run `inv version patch` to create a new version,
            or pass --force to the build command.
            """
    else:
        # copy file contents to versioned file name
        with open(ver_fname, 'wb') as fp:
            fp.write(open(source, 'rb').read())

    return ver_fname


@task(
    aliases=['ver'],
    autoprint=True,     # print return value
)
def version(ctx):
    "Print this package's version number."
    return Package().version


@task(autoprint=True)
def upversion(ctx, major=False, minor=False, patch=False):
    """Update package version (default patch-level increase).
    """
    if not (major or minor or patch):
        patch = True
    return Package().upversion(major, minor, patch)


@task
def update_template_version(ctx, fname=None):
    """Update version number in include template.
    """
    if not hasattr(ctx, 'pkg'):
        ctx.pkg = Package()
    if not hasattr(ctx.pkg, 'update_template_version_fname'):
        _t = 'templates/{pkg.name}/{pkg.name}-css.html'.format(pkg=ctx.pkg)
        ctx.pkg.update_template_version_fname = _t
        
    fname = fname or ctx.pkg.update_template_version_fname

    if not os.path.exists(fname):
        Path(ctx.pkg.root).makedirs(Path(fname).dirname())
        with open(fname, 'w') as fp:
            fp.write(textwrap.dedent("""
            {% load staticfiles %}
            {% with "0.0.0" as version %}
                {# keep the above exactly as-is (it will be overwritten when compiling the css). #}
                {% with app_path="PKGNAME/PKGNAME-"|add:version|add:".min.css" %}
                    {% if debug %}
                        <link rel="stylesheet" type="text/css" href='{% static "PKGNAME/PKGNAME.css" %}'>
                    {% else %}
                        <link rel="stylesheet" type="text/css" href="{% static app_path %}">
                    {% endif %}
                {% endwith %}
            {% endwith %}
            """).replace("PKGNAME", ctx.pkg.name))
            
    with open(fname, 'r') as fp:
        txt = fp.read()

    newtxt = re.sub(
        r'{% with "(\d+\.\d+\.\d+)" as version',
        '{{% with "{}" as version'.format(ctx.pkg.version),
        txt
    )
    with open(fname, 'w') as fp:
        fp.write(newtxt)


def min_name(fname, min='.min'):
    """Adds a `.min` extension before the last file extension.
    """
    name, ext = os.path.splitext(fname)
    return name + min + ext


def version_name(fname):
    """Returns a template string containing `{version}` in the correct
       place.
    """
    if '.min.' in fname:
        pre, post = fname.split('.min.')
        return pre + '-{version}.min.' + post
    else:
        return min_name(fname, '-{version}')

ns = Collection(
    'version',
    add_version,
    version,
    upversion,
    update_template_version
)
ns.configure({
    'force': False,
    'pkg': {
        'name': '<package-name>',
        'version': '<version-string>',
    },
})
