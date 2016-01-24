# -*- coding: utf-8 -*-

import os

from yamldirs import create_files
from dktasklib import clean


def test_clean(ctx):
    files = """
        build:
            - a
            - b
            - c:
                - d
                - e
    """
    with create_files(files) as directory:
        os.chdir(directory)
        clean.clean(ctx, 'c')
        assert os.listdir('build') == ['a', 'b', 'c']
        assert os.listdir('build/c') == []
