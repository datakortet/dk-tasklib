# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import version, Package


def test_version(ctx):
    files = """
        - package.json: |
            {
                "version": "1.1.2"
            }
    """
    with create_files(files) as directory:
        assert version.version(ctx.init()) == '1.1.2'


def test_copy_to_version(ctx):
    files = """
        - package.json: |
            { "version": "1.1.2" }
        - foo.txt: hello world
    """
    with create_files(files) as directory:
        version.copy_to_version(
            ctx.init(pkg=Package()),
            'foo.txt',
            kind='pkg'
        )
        assert 'foo-1.1.2.txt' in os.listdir('.')

        with open('foo.txt', 'w') as fp:
            fp.write('goodbye world')

        # shouldn't change versioned resources..
        version.copy_to_version(
            ctx.init(pkg=Package()),
            'foo.txt',
            kind='pkg'
        )
        print open('foo-1.1.2.txt').read()
        assert open('foo-1.1.2.txt').read() == 'hello world'

        # .. update versioned resources when forcing
        version.copy_to_version(
            ctx.init(pkg=Package()),
            'foo.txt',
            kind='pkg',
            force=True
        )
        print open('foo-1.1.2.txt').read()
        assert open('foo-1.1.2.txt').read() == 'goodbye world'


def test_add_version_hash(ctx):
    files = """
        - package.json: |
            { "version": "1.1.2" }
        - foo.txt
    """
    with create_files(files) as directory:
        version.copy_to_version(
            ctx.init(pkg=Package()),
            'foo.txt',
            kind='hash'
        )
        print os.listdir('.')
        assert len(os.listdir('.')) == 3
