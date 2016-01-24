# -*- coding: utf-8 -*-
import importlib
import inspect
import os
import textwrap

import invoke
import itertools
from docutils import nodes
from docutils.statemachine import StringList
from invoke.cli import indent_num, indent
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

    # def print_columns(self, tuples):
    #     """
    #     Print tabbed columns from (name, help) tuples.
    #
    #     Useful for listing tasks + docstrings, flags + help strings, etc.
    #     """
    #     padding = 3
    #     # Calculate column sizes: don't wrap flag specs, give what's left over
    #     # to the descriptions.
    #     name_width = max(len(x[0]) for x in tuples)
    #     desc_width = 80 - name_width - indent_num - padding - 1
    #     wrapper = textwrap.TextWrapper(width=desc_width)
    #     res = ""
    #     for name, help_str in tuples:
    #         # Wrap descriptions/help text
    #         help_chunks = wrapper.wrap(help_str)
    #         # Print flag spec + padding
    #         name_padding = name_width - len(name)
    #         spec = ''.join((
    #             indent,
    #             name,
    #             name_padding * ' ',
    #             padding * ' '
    #         ))
    #         # Print help text as needed
    #         if help_chunks:
    #             res += spec + help_chunks[0] + '\n'
    #             for chunk in help_chunks[1:]:
    #                 res += (' ' * len(spec)) + chunk + '\n'
    #         else:
    #             res += spec.rstrip() + '\n'
    #     return res

    def _options(self, tuples):
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
            classes=['urlconfig'])

        return table

    def _document_task(self, name, task, ctx):
        # import pprint
        # pprint.pprint(task.__dict__)
        # for arg in task.get_arguments(): print str(arg)
        task_name = nodes.paragraph()
        self.state.nested_parse(
            StringList([
                'task: **{}**'.format(name),
                '*(default)*' if task.is_default else ""
            ]),
            0,
            task_name
        )
        res = [task_name]

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
        # print "TUPLES:", tuples
        if tuples:
            # print self.print_columns(tuples)
            res.append(nodes.block_quote('', self._options(tuples)))
        return res

    def run(self):
        import pprint; pprint.pprint(self.__dict__)
        module_path = self.arguments[0]
        module = importlib.import_module(module_path)
        parent = os.path.dirname(module.__file__)
        collection = invoke.Collection.from_module(module, loaded_from=parent)
        parser = Parser(contexts=collection.to_contexts())
        # print "PARSER contexts:", parser.contexts

        # module_title = nodes.title()
        module_title = nodes.subtitle()
        self.state.nested_parse(
            StringList([':mod:`{}`'.format(collection.name)]),
            0,
            module_title
        )

        tasks = [(not t.is_default, name, t, parser.contexts[name])
                 for name, t in collection.tasks.items()]
        tasks.sort()
        res = [module_title]
        for _, name, t, ctx in tasks:
            res += self._document_task(name, t, ctx)
        return res
        # tasks = [self._document_task(name, t)
        #          for name, t in collection.tasks.items()]
        # return [module_title] + list(itertools.chain.from_iterable(tasks))

"""
                # 'default ' if cls.is_default else '',
                # '(c)' if cls.contextualized else '',
                # 'task: **{clsname}**'.format(clsname=clsname),
                '',

"""

def setup(app):
    app.add_directive('autotaskdoc', AutoTaskdocDirective)
