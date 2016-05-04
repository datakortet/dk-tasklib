# -*- coding: utf-8 -*-
import inspect
import os
import pprint

from dkfileutils.path import Path

from .docutils import _import, synopsis
from .crcfile import CRCFile


class Module(object):
    def __init__(self, pkg):
        self._module = None
        self._has = set()
        self._views = None
        self._output = ""

        self.path = pkg.root
        self.name = pkg.name
        self.docspath = pkg.docsdir
        self.module_name = pkg.modulename
        self.docstring = inspect.getdoc(self.module) or ""
        self.synopsis = synopsis(self.docstring)
        self.fp = CRCFile(self.rst_fname())

    def rst_fname(self):
        return os.path.join(self.docspath, self.name + '.rst')

    def close(self):
        self.fp.close()

    def _seen(self, fname):
        self._has.add(Path(fname).splitext()[0])

    def has(self, fname):
        self._seen(fname)
        return (self.path / fname).isfile()

    @property
    def module(self):
        if not self._module:
            self._module = _import(self.module_name)
        return self._module

    def _files(self):
        for fname in self.path.glob('**/*.py'):
            if '__' not in str(fname):
                root, ext = fname.splitext()
                pyname = os.path.dirname(root)
                modname = '%s.%s' % (self.module_name, pyname)
                yield pyname, modname

    def files(self):
        for pyname, modname in self._files():
            if pyname in self._has:
                continue
            yield pyname, modname

    def views(self):
        if self._views is None:
            self._views = []
            for pyname, modname in self.files():
                if pyname.endswith('views'):
                    self._views.append((pyname, modname))
                    self._seen(pyname)
        return self._views

    def __repr__(self):
        return pprint.pformat(self.__dict__)
