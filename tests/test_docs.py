# -*- coding: utf-8 -*-
import os

from yamldirs import create_files
from dktasklib import docs, Package


def test_build(ctx):
    files = """
    mypackage:
        package.json: |
            {"version": "1.2.3"}
        docs:
            - conf.py: |
                master_doc = 'index'
            - index.rst: |
                hello *world*

                .. toctree::
                   modules

                .. include:: modules.rst

    """
    with create_files(files) as directory:
        os.chdir('mypackage')
        ctx = ctx.init(pkg=Package())
        docs.build(ctx, clean=True)  # cover clean when clean.
        ctx.run('tree')
        assert os.path.exists('build/docs/index.html')
        assert '<p>hello <em>world</em></p>' in open('build/docs/index.html').read()

        # cover clean when dirty
        docs.build(ctx, clean=True, warn=True)
        assert os.path.exists('build/docs/index.html')
        assert '<p>hello <em>world</em></p>' in open('build/docs/index.html').read()
