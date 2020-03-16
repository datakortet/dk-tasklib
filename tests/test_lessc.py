# -*- coding: utf-8 -*-
from __future__ import print_function
import os

import invoke
from yamldirs import create_files

from dktasklib import Package
from dktasklib import lessc
from dktasklib.commands import tree


def test_less_simple(ctx):
    files = """
        foo.less: |
            .foo {
                display: flex;
            }
    """
    with create_files(files) as directory:
        assert 'foo.css' not in os.listdir('.')
        print(lessc.lessc(
            ctx.init(), src='foo.less', dst='foo.css',
            autoprefix="ie > 8, last 4 versions"
        ))
        assert 'foo.css' in os.listdir('.')
        csstxt = open('foo.css').read()
        print(csstxt)
        # assert len(open('foo.css').read()) > len(open('foo.less').read())
        assert '-ms-flexbox' in csstxt

def test_less_rule_default(ctx):
    # standard package structure..
    files = """
    mypackage:
        - package.json: |
            {"version": "1.2.3"}
        - setup.py
        - mypackage:
            - less:
                mypackage.less: |
                    .foo {
                        display: flex;
                        color: lighten(red, 20%);
                    }
    """
    with create_files(files) as directory:
        os.chdir('mypackage')  # into the package directory

        ctx = ctx.init(pkg=Package())

        lessc.LessRule(ctx)
        tree()
        # .
        # |-- mypackage
        # |   |-- less
        # |   |   `-- mypackage.less
        # |   |-- static
        # |   |   `-- mypackage
        # |   |       `-- css
        # |   |           |-- mypackage-1.2.3.min.css
        # |   |           `-- mypackage.css
        # |   `-- templates
        # |       `-- mypackage
        # |           `-- mypackage-css.html    # due to `after` task
        # |-- package.json
        # `-- setup.py

        assert 'mypackage.css' in os.listdir('mypackage/static/mypackage/css')
        assert 'mypackage-1.2.3.min.css' in os.listdir('mypackage/static/mypackage/css')
        assert 'mypackage-css.html' in os.listdir('mypackage/templates/mypackage')


def test_less_rule_non_std(ctx):
    # standard package structure..
    files = """
    mypackage:
        - package.json: |
            {"version": "1.2.3"}
        - setup.py
        - mypackage:
            - less:
                mypackage-bs3.less: |
                    .foo {
                        display: flex;
                        color: lighten(red, 20%);
                    }
    """
    with create_files(files) as directory:
        os.chdir('mypackage')  # into the package directory

        ctx = ctx.init(pkg=Package())

        lessc.LessRule(
            ctx,
            src='mypackage/less/mypackage-bs3.less',
            dst='mypackage/static/mypackage/css/mypackage-bs3-{version}.min.css',
            import_fname='mypackage/templates/mypackage/mypackage-bs3-css.html'
        )
        tree()
        # .
        # |-- mypackage
        # |   |-- less
        # |   |   `-- mypackage-bs3.less
        # |   |-- static
        # |   |   `-- mypackage
        # |   |       `-- css
        # |   |           |-- mypackage-bs3-1.2.3.min.css
        # |   |           `-- mypackage-bs3.css
        # |   `-- templates
        # |       `-- mypackage
        # |           `-- mypackage-bs3-css.html
        # |-- package.json
        # `-- setup.py
        assert 'mypackage-bs3.css' in os.listdir('mypackage/static/mypackage/css')
        assert 'mypackage-bs3-1.2.3.min.css' in os.listdir('mypackage/static/mypackage/css')
        assert 'mypackage-bs3-css.html' in os.listdir('mypackage/templates/mypackage')

