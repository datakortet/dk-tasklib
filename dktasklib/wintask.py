# -*- coding: utf-8 -*-
import os
import sys

try:
    from invoke import ctask as _task
except ImportError:
    from invoke import task as _task

from invoke import Context

if not getattr(Context, '_patched', False):
    Context._patched = True
    _orig_run = Context.run

    def run(self, command, **kwargs):
        if sys.platform == 'win32':
            kwargs['shell'] = os.environ['COMSPEC']
        return _orig_run(self, command, **kwargs)

    Context.run = run

task = _task
