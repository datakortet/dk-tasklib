# -*- coding: utf-8 -*-
"""
Automatically document pyinvoke task libraries.

Usage
-----

Assuming your directory structure is as follows::

    .
    ├── myproject
    │   ├── bar.py
    │   ├── foo.py
    │   └── __init__.py
    └── setup.py

Run::

    sphinx-quickstart

The rest of this text assumes that you set the documentation root to ``docs``,
leave the master document as ``index``, and hat you enable the autodoc sphinx
extension. Your directory will now look something like (I've used the default
for most options to keep it simple):

    .
    ├── docs
    │   ├── _build
    │   ├── conf.py
    │   ├── index.rst
    │   ├── make.bat
    │   ├── Makefile
    │   ├── _static
    │   └── _templates
    ├── myproject
    │   ├── bar.py
    │   ├── foo.py
    │   └── __init__.py
    └── setup.py

Next, run::

    sphinx-apidoc -o docs/api myproject

and your directory tree will look like::

    .
    ├── docs
    │   ├── api
    │   │   ├── modules.rst
    │   │   └── myproject.rst
    │   ├── conf.py
    │   ├── ...
    └── setup.py

Add this module under ``docs/ext/autotask/autotask.py`` and edit
``docs/conf.py` so sphinx can find it::

    sys.path.insert(0, os.path.abspath('..'))

    extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.napoleon',  # must be after autodoc..
        ...
        'ext.autotaskdoc',
    ]

Finally, edit the ``docs/index.rst`` file::

    myproject
    =========

    .. toctree::
       :maxdepth: 2

       api/myproject

and add the ``autotaskdoc`` directive to any modules containing tasks in
``docs/api/myproject.rst``::

    myproject package
    =================

    Submodules
    ----------

    myproject.bar module
    --------------------

    .. automodule:: myproject.bar
        :members:
        :undoc-members:
        :show-inheritance:

    .. autotaskdoc:: myproject.bar

"""


import importlib
import inspect
import os

import invoke
from docutils import nodes
from docutils.statemachine import StringList
from invoke.parser import Parser
from sphinx.util.compat import Directive


class AutoTaskdocDirective(Directive):
    """Directive to display documentation for a pyinvoke task.
    """
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {}

    def _options(self, tuples):
        # output the task's options as a two-column table
        rows = []
        for k, v in tuples:
            namecell = nodes.literal('', k)
            helpcell = nodes.paragraph()
            self.state.nested_parse(StringList([v]), 0, helpcell)
            rows.append(
                nodes.row(
                    '',
                    nodes.entry('', namecell),
                    nodes.entry('', helpcell)
                )
            )
        table = nodes.table(
            '',
            nodes.tgroup(
                '',
                nodes.colspec(colwidth=40),
                nodes.colspec(colwidth=40),
                nodes.thead(
                    '',
                    nodes.row(
                        '',
                        nodes.entry('', nodes.paragraph('', 'options')),
                        nodes.entry('', nodes.paragraph('', '')))),
                nodes.tbody('', *rows)),
            classes=['task-options'])

        return table

    def _document_task(self, name, task, ctx):
        # output name of task, and note if it is the default task
        task_name = nodes.paragraph(classes=['task-name'])
        self.state.nested_parse(
            StringList([
                'task: **{}**'.format(name),
                '*(default)*' if task.is_default else ""
            ]),
            0,
            task_name
        )
        res = [task_name]

        # output the task's docstring
        getdoc = inspect.getdoc(task)
        if getdoc is not None:
            docstring = nodes.block_quote()
            self.state.nested_parse(
                StringList(getdoc.split('\n')),
                0,
                docstring
            )
            res.append(docstring)

        tuples = ctx.help_tuples()
        if tuples:
            res.append(nodes.block_quote('', self._options(tuples)))
        return res

    def run(self):
        # import pprint; pprint.pprint(self.__dict__)
        module_path = self.arguments[0]
        module = importlib.import_module(module_path)
        parent = os.path.dirname(module.__file__)
        collection = invoke.Collection.from_module(module, loaded_from=parent)
        parser = Parser(contexts=collection.to_contexts())

        # output the name of the collection
        module_title = nodes.subtitle()
        self.state.nested_parse(
            StringList([':mod:`{}` *tasks*'.format(collection.name)]),
            0,
            module_title
        )

        # sort tasks alphabetically, except default task should be first.
        tasks = [(not t.is_default, name, t, parser.contexts[name])
                 for name, t in collection.tasks.items()]
        tasks.sort()
        if not tasks:
            return []

        res = [module_title]
        for _, name, t, ctx in tasks:
            res += self._document_task(name, t, ctx)
        return res


def setup(app):
    app.add_directive('autotaskdoc', AutoTaskdocDirective)
