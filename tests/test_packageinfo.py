import os

from yamldirs import create_files

from dktasklib import package


def test_package_info(ctx):
    files = """
        setup.py: |
            from setuptools import setup
            setup(version='1.1.2')
        subdir: []
    """
    with create_files(files) as directory:
        package.package(ctx.init())
        assert True
