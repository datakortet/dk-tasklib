# -*- coding: utf-8 -*-
import json
import os
import invoke
import pytest
from yamldirs import create_files

from dktasklib import version, package


def test_find_package():
    files = """
        - package.json: |
            {
                "version": "1.1.2"
            }
        - subdir:
            - empty
    """
    with create_files(files) as directory:
        os.chdir(os.path.join(directory, 'subdir'))
        pkg = package.Package()
        assert pkg.version == '1.1.2'


def test_find_package2():
    files = """
        - package.json: |
            {
                "version": "1.1.2"
            }
        - subdir:
            - empty
    """
    with create_files(files) as directory:
        os.chdir(os.path.join(directory, 'subdir'))
        pkg = package.Package(directory)
        assert pkg.version == '1.1.2'


def test_attributes():
    files = """
        - package.json: |
            { "version": "1.1.2" }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        pkg = package.Package()
        assert pkg.version == '1.1.2'
        assert pkg.get('foo', 'bar') == 'bar'
        with pytest.raises(AttributeError):
            pkg.foo


def test_version():
    files = """
        - package.json: |
            {
                "version": "1.1.2"
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        pkg = package.Package()
        assert pkg.version == '1.1.2'


def test_upversion():
    files = """
        - package.json: |
            {
                "version": "1.1.2"
            }
        #- tasks.py: |
        #    from dktasklib.version import upversion
    """
    with create_files(files) as directory:
        os.chdir(directory)

        version.upversion(invoke.Context())
        print open('package.json').read()
        assert json.load(open('package.json'))['version'] == '1.1.3'

        version.upversion(invoke.Context(), minor=True)
        print open('package.json').read()
        assert json.load(open('package.json'))['version'] == '1.2.3'

        version.upversion(invoke.Context(), major=True)
        print open('package.json').read()
        assert json.load(open('package.json'))['version'] == '2.2.3'
