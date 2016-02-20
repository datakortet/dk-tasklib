# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
import json
import os
import subprocess
from ConfigParser import RawConfigParser

import invoke
import pytest
from yamldirs import create_files

import dktasklib.package.package_ini
from dktasklib import version, package


def test_find_package():
    files = """
        setup.py: |
            from distutils.core import setup
            setup(version='1.1.2')
        subdir: []
    """
    with create_files(files) as directory:
        print "\nCURDIR:", os.getcwd()
        print "CONTENTS:", os.listdir('.')
        os.chdir('subdir')
        pkg = package.Package()
        assert pkg.version == '1.1.2'


def test_attributes():
    files = """
        setup.py: |
            from distutils.core import setup
            setup(version='1.1.2')
    """
    with create_files(files) as directory:
        assert dktasklib.package.setup_file.SetupPy.exists()
        pkg = package.Package()
        assert pkg.version == '1.1.2'
        assert pkg.get('foo', 'bar') == 'bar'
        with pytest.raises(AttributeError):
            pkg.foo


def test_version():
    files = """
        setup.py: |
            from distutils.core import setup
            setup(version='1.1.2')
    """
    with create_files(files) as directory:
        pkg = package.Package()
        assert pkg.version == '1.1.2'


def _getval(attr):
    return subprocess.check_output("python setup.py --" + attr).strip()


def test_upversion():
    files = """
        setup.py: |
            from distutils.core import setup
            setup(version='1.1.2')
    """
    with create_files(files) as directory:
        os.chdir(directory)

        version.upversion(invoke.Context())
        print open('setup.py').read()
        assert _getval('version') == '1.1.3'

        version.upversion(invoke.Context(), minor=True)
        print open('setup.py').read()
        assert _getval('version') == '1.2.0'

        version.upversion(invoke.Context(), major=True)
        print open('setup.py').read()
        assert _getval('version') == '2.0.0'


