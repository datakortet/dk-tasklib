# -*- coding: utf-8 -*-
import os
import string
import sys
from contextlib import contextmanager

join = os.path.join
null = "NUL" if sys.platform == 'win32' else '/dev/null'
win32 = sys.platform == 'win32'


class _MissingDottedString(str):
    def __getattr__(self, attr):
        return _MissingDottedString(self[:-1] + '.' + attr + '}')


class _MissingContext(dict):
    def __missing__(self, key):
        return _MissingDottedString('{%s}' % key)


def fmt(s, ctx):
    """Use the mapping `ctx` as a formatter for the {new.style} formatting
       string `s`.
    """
    return string.Formatter().vformat(s, (), _MissingContext(ctx))


def switch_extension(fname, ext="", old_ext=None):
    """Switch file extension on `fname` to `ext`. Returns the resulting
       file name.

       Usage::

           switch_extension('a/b/c/d.less', '.css')
    
    """
    name, _ext = os.path.splitext(fname)
    if old_ext:
        assert old_ext == _ext
    return name + ext


def filename(fname):
    """Return only the file name (removes the path)
    """
    return os.path.split(fname)[1]


@contextmanager
def cd(directory):
    """Context manager to change directory.

       Usage::

           with cd('foo/bar'):
               # current directory is now foo/bar
           # current directory restored.

    """
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)
