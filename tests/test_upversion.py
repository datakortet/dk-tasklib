# -*- coding: utf-8 -*-
import os
import re

from yamldirs import create_files

from dktasklib import Package
from dktasklib import upversion

PACKAGE_FILES = """
mypackage:
    - package.json: |
        {"version": "1.2.3"}
    - setup.py
    - mypackage:
        - __init__.py
"""

#: Tag libraries Django has removed. ``staticfiles`` and ``admin_static``
#: were dropped in Django 3.0 (deprecated in 2.1), ``future`` in 1.10.
#: Loading one is a hard TemplateSyntaxError when the template renders.
REMOVED_TAG_LIBRARIES = {'admin_static', 'future', 'staticfiles'}

LOAD_TAG = re.compile(r'{%\s*load\s+(.*?)%}', re.DOTALL)


def loaded_libraries(source):
    """Yield every tag library name loaded by ``source``."""
    for names in LOAD_TAG.findall(source):
        names = names.split()
        # mirrors django.template.defaulttags.load, which only treats this
        # as {% load somename from somelibrary %} when 'from' is next to last
        if len(names) >= 3 and names[-2] == 'from':
            yield names[-1]
        else:
            for name in names:
                yield name


def scaffold_css_template(ctx):
    """Run UpdateTemplateVersion on a fresh package, return the template."""
    fname = '{pkg.source}/templates/{pkg.name}/{pkg.name}-css.html'
    rule = upversion.UpdateTemplateVersion()
    rule.ctx = ctx.init(pkg=Package())
    rule(fname)
    with open(fname.format(pkg=rule.ctx.pkg)) as fp:
        return fp.read()


def test_scaffolded_template_loads_no_removed_tag_library(ctx):
    """The generated template must not {% load %} a removed library."""
    with create_files(PACKAGE_FILES):
        os.chdir('mypackage')
        template = scaffold_css_template(ctx)

    loaded = set(loaded_libraries(template))
    assert not loaded & REMOVED_TAG_LIBRARIES
    assert 'static' in loaded


def test_scaffolded_template_gets_the_package_version(ctx):
    """The version placeholder is rewritten to the package version."""
    with create_files(PACKAGE_FILES):
        os.chdir('mypackage')
        template = scaffold_css_template(ctx)

    assert '{% with "1.2.3" as version %}' in template
