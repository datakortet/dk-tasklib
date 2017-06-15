# -*- coding: utf-8 -*-

"""Package based on package.json
"""
import json
import os
from dkfileutils.pfind import pfind
from .package_interface import PackageInterface


class PackageJson(PackageInterface):
    """Read package.json file::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """
    @classmethod
    def exists(cls):
        return pfind('.', 'package.json')

    def __init__(self, ctx=None, fname='package.json'):
        fname = pfind('.', fname)
        super(PackageJson, self).__init__(ctx, fname=fname)
        self._package = None

    @property
    def package(self):
        if not self._package:
            with open(self.fname) as fp:
                self._package = json.loads(fp.read())
        return self._package

    def save(self):
        json.dump(self.package, open(self.fname, 'w'), indent=4)

    def __iter__(self):
        return iter(self.package.items())

    def _get(self, attr):
        if not self.fname:
            raise AttributeError(attr)
        return self.package[attr]

    def get(self, attr, default=None):
        try:
            return self._get(attr)
        except (AttributeError, KeyError):
            return super(PackageJson, self).get(attr, default)

    def set(self, key, value):
        self.package[key] = value
