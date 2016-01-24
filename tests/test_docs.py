# -*- coding: utf-8 -*-
import os

from yamldirs import create_files


def test_lessc(ctx):
    files = """
        docs: |
            .foo {
                display: flex;
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
