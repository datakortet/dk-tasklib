# -*- coding: utf-8 -*-
from __future__ import print_function
import os

import sys
from yamldirs import create_files

from dktasklib.commands import tree
from dktasklib.publish import publish


def test_publish(ctx):
    files = """
    mypackage:
        - setup.py: |
            from distutils.core import setup
            setup(
                name='mypackage',
                packages=['mypackage'],
                version='1.0.0',
                url='http://example.com',
                author='Test Testham',
                author_email='test@example.com',
            )
        - README: |
            this is readme
        - MANIFEST: |
            README
            setup.cfg
            setup.py
            mypackage/__init__.py
            mypackage/foo.py
        - setup.cfg: |
            [wheel]
            universal = 1
        - mypackage:
            - __init__.py
            - foo.py: |
                def foo(x):  print 'foo', x
        - docs:
            - index.rst: |
                hello world
                -----------
    """
    with create_files(files, cleanup=True) as directory:
        print("DIRECTORY:", directory)
        os.chdir('mypackage')  # into the package directory
        ctx = ctx.init(echo=True)
        publish(ctx, wheel=False)
        ctx.run('tree')
        assert 'mypackage-1.0.0.tar.gz' in os.listdir('dist')
