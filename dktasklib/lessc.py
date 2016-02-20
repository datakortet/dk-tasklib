# -*- coding: utf-8 -*-
import os

from dkfileutils.changed import Directory
from dkfileutils.path import Path
from invoke import ctask as task, Collection

from dktasklib.concat import copy
from dktasklib.environment import env
from . import urlinliner
from .executables import requires
from .utils import switch_extension, fmt
from .version import get_version
from .version import update_template_version


@requires('nodejs', 'npm', 'lessc')
def lessc(ctx,
          source, destination="",
          include_path=None,
          strict_imports=False,
          inline_urls=True,
          autoprefix=True,
          cleancss=True):
    """Run `lessc` with options.

       Args:
           source (str): the input file name
           destination (Optional[str]): the output filename (if not specified
                it will be the same as the input file name and a ``.css``
                extension).
           include_path (Optional[List[str]]): Optional list of directories
                to search to satisfy ``@import`` directives.
           strict_imports (bool): Re-fetch all imports.
           inline_urls (bool): Should ``@url(.../foo.png)`` be inlined?
           autoprefix (bool): Should the autoprefixer be run (last 4 versions)
           cleancss (bool): Should the css be minified?

       Returns:
           str: The output file name.

    """
    if include_path is None:
        include_path = []
    if not destination:
        destination = switch_extension(source, '.css', '.less')
    options = ""
    if getattr(ctx, 'verbose', False):  # pragma: nocover
        options += ' --verbose'
    if include_path:
        options += ' --include-path="%s"' % ';'.join(include_path)
    if strict_imports:
        options += " --strict-imports"
    if inline_urls:
        options += " --inline-urls"
    if autoprefix:
        options += ' --autoprefix="last 4 versions"'
    if cleancss:
        options += ' --clean-css="-b --s0 --advanced"'

    ctx.run("lessc {options} {source} {destination}".format(**locals()))
    return destination


# noinspection PyIncorrectDocstring
@task(
    default=True,
    post=[update_template_version]
)
def build_less(ctx,
               source='{pkg.sourcedir}/less/{pkg.name}.less',
               dest='{pkg.sourcedir}/static/{pkg.name}/css/{pkg.name}-{version}.min.css',
               version='pkg',
               bootstrap=True,
               force=False,
               **kw):
    """Build a ``.less`` file into a versioned and minified ``.css`` file.

       Args:
           ctx (Context):    automatically passed by invoke.
           source (str):     input file name (can contain {template} strings
                             that will be looked up in env.
           dest (str):       output file name (ditto about template strings).
           version (str):    the type of version number (pkg or hash)
           bootstrap (bool): Should Bootstrap be compiled in?
           force (bool):     Rebuild even if nothing has changed.

       Returns:
           str:              dest file name fully instantiated with
                             template parameters

    """
    c = env(ctx)
    source = Path(fmt(source, c))
    dest = Path(fmt(dest, c))

    for fname in source.dirname().glob("*.inline"):
        urlinliner.inline(ctx, fname)

    if not force and not Directory(source.dirname()).changed(glob='**/*.less'):
        print "No changes: {input_dir}/{glob}, add --force to build.".format(
            input_dir=source.dirname(), glob='**/*.less')
        return

    path = kw.pop('path', [])
    if (bootstrap or ctx.lessc.use_bootstrap) and ctx.bootstrap.src:
        path.append(ctx.bootstrap.src)

    cssname = lessc(
        ctx,
        source.relpath(),
        dest.relpath().format(version=get_version(ctx, source, version)),
        include_path=path,
        strict_imports=True,
        inline_urls=False,
        autoprefix=True,
        cleancss=True,
    )

    copy(  # create a copy without version number too..
        ctx,
        cssname,
        Path(cssname).dirname() / switch_extension(source.basename(), '.css'),
        force=True
    )
    return cssname


ns = Collection('lessc', build_less)
ns.configure({
    'force': False,
    'pkg': {
        'root': '<package-root-directory>',
        'name': '<package-name>',
        'sourcedir': '<source-dir>',
        'version': '<version-string>',
    },
    'bootstrap': {
        'src': os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less'),
    },
    'lessc': {
        'use_bootstrap': False,
        'build_dir': 'build/css',
        'input_dir': '{pkg.sourcedir}/less',
        'input_fname': '{pkg.name}.less',
        'output_dir': '{pkg.sourcedir}/static/{pkg.name}/css/',
        'output_fname': '{pkg.name}.css',
    }
})
