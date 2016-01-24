# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import lessc


def test_less_version(ctx):
    v = lessc.version(ctx)
    print v
    assert v


def test_lessc(ctx):
    files = """
        foo.less: |
            .foo {
                display: flex;
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        assert lessc.lessc(ctx, 'foo.less') == 'foo.css'
        assert 'foo.css' in os.listdir('.')
        print open('foo.css').read()
        assert len(open('foo.css').read()) > len(open('foo.less').read())
