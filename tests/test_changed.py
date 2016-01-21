# -*- coding: utf-8 -*-
import os

from yamldirs import create_files

from dktasklib import changed


def test_dirchange():
    files = """
        - foo:
            - bar
    """
    with create_files(files) as directory:
        os.chdir(directory)
        count = 0
        print os.listdir('.')
        print os.listdir('foo')
        with changed.changed_dir('foo'):
            count += 1
        assert count == 1
        with changed.changed_dir('foo'):
            count += 1
        assert count == 1
