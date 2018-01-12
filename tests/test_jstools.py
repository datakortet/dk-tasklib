# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import Package
from dktasklib.jstools import babel, version_js


def test_babel(ctx):
    files = """
        - package.json: |
            { "version": "1.1.2", "description": "",
              "repository": "", "license": ""}
        - foo.js: |
            [1,2,3].map(x => x*x)
    """
    with create_files(files) as directory:
        ctx = ctx.init(pkg=Package())
        babel(
            ctx,
            'foo.js',
            'foo-compiled.js',
        )
        output = open('foo-compiled.js').read()
        assert 'function (x)' in output
        assert 'return' in output


def test_version_js(ctx):
    fname = 'dkuser/static/js/create-user.js'
    assert version_js(ctx, fname) == ''


def test_babel2(ctx):
    files = """
        - foo.js: |
            [1,2,3].map(x => x*x)
    """
    with create_files(files) as directory:
        ctx = ctx.init(pkg=Package())
        babel(
            ctx,
            'foo.js',
            'foo-compiled.js',
        )
        output = open('foo-compiled.js').read()
        assert 'function (x)' in output
        assert 'return' in output
