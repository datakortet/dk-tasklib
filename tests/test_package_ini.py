# -*- coding: utf-8 -*-
import json
import os
from ConfigParser import RawConfigParser

import invoke
import pytest
from yamldirs import create_files

import dktasklib.package.package_ini
from dktasklib import upversion, package


def test_find_package():
    files = """
        - package.ini: |
            [package]
            version = 1.1.2
        - subdir:
            - empty
    """
    with create_files(files) as directory:
        os.chdir(os.path.join(directory, 'subdir'))
        pkg = package.Package()
        assert pkg.version == '1.1.2'


def test_find_package2():
    files = """
        - package.ini: |
            [package]
            version = 1.1.2
        - subdir:
            - empty
    """
    with create_files(files) as directory:
        os.chdir(os.path.join(directory, 'subdir'))
        pkg = package.Package(directory)
        assert pkg.version == '1.1.2'


def test_attributes():
    files = """
        - package.ini: |
            [package]
            version = 1.1.2
    """
    with create_files(files) as directory:
        # os.chdir(directory)
        assert dktasklib.package.package_ini.PackageIni.exists()
        pkg = package.Package()
        assert pkg.version == '1.1.2'
        assert pkg.get('foo', 'bar') == 'bar'
        with pytest.raises(AttributeError):
            pkg.foo


def test_version():
    files = """
        - package.ini: |
            [package]
            version = 1.1.2
    """
    with create_files(files) as directory:
        # os.chdir(directory)
        pkg = package.Package()
        assert pkg.version == '1.1.2'


def _getval(fname, attr):
    p = RawConfigParser()
    p.read(fname)
    return p.get('package', attr)


def test_upversion():
    files = """
        - package.ini: |
            [package]
            version = 1.1.2
        #- tasks.py: |
        #    from dktasklib.version import upversion
    """
    with create_files(files) as directory:
        # os.chdir(directory)

        upversion.upversion(invoke.Context())
        print open('package.ini').read()
        assert _getval('package.ini', 'version') == '1.1.3'

        upversion.upversion(invoke.Context(), minor=True)
        print open('package.ini').read()
        assert _getval('package.ini', 'version') == '1.2.0'

        upversion.upversion(invoke.Context(), major=True)
        print open('package.ini').read()
        assert _getval('package.ini', 'version') == '2.0.0'
