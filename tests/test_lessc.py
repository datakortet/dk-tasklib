# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import lessc


def test_lessc():
    files = """
        foo.less: |
            .foo {
                display: flex;
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        lessc.lessc(
            invoke.Context(),
            'foo.less'
        )
        assert 'foo.css' in os.listdir('.')
        assert len(open('foo.css').read()) > len(open('foo.less').read())
        # for fname in os.listdir('.'):
        #     print open(fname).read()
