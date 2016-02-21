# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import docs


def test_build(ctx):
    files = """
        docs:
            - conf.py: |
                master_doc = 'index'
            - index.rst: |
                hello *world*
    """
    with create_files(files) as directory:
        ctx = ctx.init(
            docs=dict(
                source='docs',
                builddir='build',
                target_file='index.html'
            )
        )
        # ctx.docs = invoke.Config()
        # ctx.docs.source = 'docs'
        # ctx.docs.builddir = 'build'
        # ctx.docs.target_file = 'index.html'
        docs.build(ctx, clean=True)  # cover clean when clean.
        docs.tree(ctx)
        assert os.path.exists('build/index.html')
        assert '<p>hello <em>world</em></p>' in open('build/index.html').read()

        # cover clean when dirty
        docs.build(ctx, clean=True, warn=True)
        assert os.path.exists('build/index.html')
        assert '<p>hello <em>world</em></p>' in open('build/index.html').read()
