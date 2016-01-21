# -*- coding: utf-8 -*-
import inspect
import os
from contextlib import contextmanager

import sys

from dkfileutils.changed import changed

join = os.path.join


def switch_extension(fname, ext="", old_ext=None):
    """Usage::
    
            switch_extension('a/b/c/d.less', '.css')
    
    """
    name, _ext = os.path.splitext(fname)
    if old_ext:
        assert old_ext == _ext
    return name + ext


def filename(fname):
    return os.path.split(fname)[1]


def min_name(fname, min='.min'):
    name, ext = os.path.splitext(fname)
    return name + min + ext


def version_name(fname):
    if '.min.' in fname:
        pre, post = fname.split('.min.')
        return pre + '-{version}.min.' + post
    else:
        return min_name(fname, '-{version}')
    

@contextmanager
def cd(directory):
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)
