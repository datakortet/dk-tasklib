# -*- coding: utf-8 -*-
import os
import re
import textwrap

import invoke
from dkfileutils.changed import Directory
from dkfileutils.path import Path
from invoke import ctask as task, Collection
from dktasklib import urlinliner
from dktasklib.concat import copy
from dktasklib.environment import env
from dktasklib.lessc import lessc
from dktasklib.utils import fmt, switch_extension
from dktasklib.version import update_template_version, get_version


SRV = Path(os.environ['SRV'])


class State(object):
    pass


class FileExists(State):
    def __init__(self, fname):
        self.fname = fname

    def run(self):
        return os.path.exists(self.fname)


class BuildRule(object):
    requires = []
    after = []
    _temp_mark = _perm_mark = False

    def __init__(self, *args, **kwargs):
        # print "name:", self.__class__.__name__
        # print "ARGS:", args
        # print "KW:", kwargs
        self.ctx = None
        self.kwargs = kwargs
        self.args = ()
        if len(args) == 0:
            return

        ctx = None
        first, rest = args[0], args[1:]
        if isinstance(first, invoke.Context):
            ctx = first
            self.args = rest
        else:
            self.args = args

        if ctx is not None:
            self.run(ctx)

    def run(self, ctx):
        self.ctx = ctx
        for task_obj in self.topsort(self.requires):
            task_obj.run(ctx)

        if self.needs_to_run():
            self(*self.args, **self.kwargs)
            for task_obj in self.topsort(self.after):
                task_obj.run(ctx)

    def __call__(self, *args, **kwargs):
        raise NotImplemented

    def needs_to_run(self):
        return True

    def topsort(self, tasklist):
        """Topological sort
        """
        tasks = {id(t): t for t in tasklist}
        res = []

        def visit(name, task):
            if task._temp_mark:
                raise ValueError("Circularity", name, res)
            if not task._perm_mark:
                task._temp_mark = True
                for d in task.requires:
                    visit(d, tasks[d])
                task._perm_mark = True
                task._temp_mark = False
                res.append(name)

        while 1:
            unmarked = set((name, task) for name, task in tasks.items()
                           if not (task._perm_mark or task._temp_mark))
            if not unmarked:
                return [tasks[k] for k in res]
            name, task = unmarked.pop()
            visit(name, task)

    def xtopsort(self, tasklist):
        """Topological sort
        """
        tasks = {t.__name__: t for t in tasklist}
        res = []

        def visit(name, task):
            if task._temp_mark:
                raise ValueError("Circularity", name, res)
            if not task._perm_mark:
                task._temp_mark = True
                for d in task.requires:
                    visit(d, tasks[d])
                task._perm_mark = True
                task._temp_mark = False
                res.append(name)

        while 1:
            unmarked = set((name, task) for name, task in tasks.items()
                           if not (task._perm_mark or task._temp_mark))
            if not unmarked:
                return [tasks[k] for k in res]
            name, task = unmarked.pop()
            visit(name, task)


class UpdateTemplateVersion(BuildRule):
    def __call__(self, fname=None):
        fname = fname or '{pkg.sourcedir}/templates/{pkg.name}/{pkg.name}-css.html'.format(**self.ctx)

        if not os.path.exists(fname):
            Path(self.ctx.pkg.root).makedirs(Path(fname).dirname())
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
                """).replace("PKGNAME", self.ctx.pkg.name))

        with open(fname, 'r') as fp:
            txt = fp.read()

        newtxt = re.sub(
            r'{% with "(\d+\.\d+\.\d+)" as version',
            '{{% with "{}" as version'.format(self.ctx.pkg.version),
            txt
        )
        with open(fname, 'w') as fp:
            fp.write(newtxt)
        print 'Updated {% import %} template:', fname


@task(
    default=True,
    help={
        'version': "one of pkg|hash|svn",
    }
)
class LessRule(BuildRule):
    """Build a ``.less`` file into a versioned and minified ``.css`` file.
    """
    after = [UpdateTemplateVersion()]
    bootstrap_src = SRV / 'lib' / 'bootstrap' / 'less'

    def __call__(self,
                 source='{pkg.sourcedir}/less/{pkg.name}.less',
                 dest='{pkg.sourcedir}/static/{pkg.name}/css/{pkg.name}-{version}.min.css',
                 version='pkg',
                 bootstrap=True,
                 force=False,
                 **kw):
        c = env(self.ctx)
        source = Path(fmt(source, c))
        dest = Path(fmt(dest, c))

        for fname in source.dirname().glob("*.inline"):
            urlinliner.inline(self.ctx, fname)

        if not force and not Directory(source.dirname()).changed(glob='**/*.less'):
            print "No changes: {input_dir}/{glob}, add --force to build.".format(
                input_dir=source.dirname(), glob='**/*.less')
            return

        path = kw.pop('path', [])
        if bootstrap:
            path.append(self.bootstrap_src)

        cssname = lessc(
            self.ctx,
            source.relpath(),
            dest.relpath().format(version=get_version(self.ctx, source, version)),
            include_path=path,
            strict_imports=True,
            inline_urls=False,
            autoprefix=True,
            cleancss=True,
        )

        copy(  # create a copy without version number too..
            self.ctx,
            cssname,
            Path(cssname).dirname() / switch_extension(source.basename(), '.css'),
            force=True
        )
        return cssname


ns = Collection('rule', LessRule)

# @task
# class CreateFoo(BuildRule):
#     """Create foo.txt
#     """
#     requires = [FileExists('foo.txt')]
#
#     def needs_to_run(self):
#         # return False
#         return not os.path.exists('foo.txt') or int(open('foo.txt').read()) < time.time()
#
#     def __call__(self, name):
#         print "name:", name
#         with open('foo.txt', 'w') as fp:
#             print >>fp, int(time.time())
#         self.ctx.run('echo foo')
#         print 'foo:', open('foo.txt').read()
