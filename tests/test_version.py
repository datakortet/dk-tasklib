# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import version


def test_version(ctx):
    files = """
        - package.json: |
            {
                "version": "1.1.2"
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        assert version.version(ctx) == '1.1.2'


def test_add_version():
    files = """
        - package.json: |
            { "version": "1.1.2" }
        - foo.txt: hello world
    """
    with create_files(files) as directory:
        os.chdir(directory)

        version.add_version(
            invoke.Context(),
            'foo.txt',
            'foo-{version}.txt',
            'pkg'
        )
        assert os.path.exists('foo-1.1.2.txt')

        with open('foo.txt', 'w') as fp:
            fp.write('goodbye world')

        # shouldn't change versioned resources..
        version.add_version(
            invoke.Context(),
            'foo.txt',
            'foo-{version}.txt',
            'pkg'
        )
        print open('foo-1.1.2.txt').read()
        assert open('foo-1.1.2.txt').read() == 'hello world'

        # .. update versioned resources when forcing
        version.add_version(
            invoke.Context(),
            'foo.txt',
            'foo-{version}.txt',
            'pkg',
            force=True
        )
        print open('foo-1.1.2.txt').read()
        assert open('foo-1.1.2.txt').read() == 'goodbye world'


def test_add_version_hash():
    files = """
        - package.json: |
            { "version": "1.1.2" }
        - foo.txt
    """
    with create_files(files) as directory:
        os.chdir(directory)
        version.add_version(
            invoke.Context(),
            'foo.txt',
            'foo-{version}.txt',
            'hash'
        )
        print os.listdir('.')
        assert len(os.listdir('.')) == 3


def test_update_template_version():
    files = """
        - package.json: |
            {
                "name": "foo",
                "version": "1.1.2"
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        version.update_template_version(
            invoke.Context()
        )
        assert 1
