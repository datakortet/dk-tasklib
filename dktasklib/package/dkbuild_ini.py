# -*- coding: utf-8 -*-

"""Package based on dkbuild.ini
"""
from ConfigParser import NoOptionError, RawConfigParser

from dkfileutils.pfind import pfind

from .package_json import PackageJson
from .setup_file import SetupPy
from .package_interface import PackageInterface


class DkbuildIni(PackageInterface):
    fallback_modules = [m for m in [PackageJson, SetupPy] if m.exists()]

    @classmethod
    def exists(cls):
        return pfind('.', 'dkbuild.ini')

    def __init__(self, ctx=None, fname='dkbuild.ini'):
        self._package = None
        fname = pfind('.', fname or 'dkbuild.ini')
        super(DkbuildIni, self).__init__(ctx, fname=fname)

    @property
    def package(self):
        if self._package is None:
            self._package = RawConfigParser()
            self._package.read(self.fname)
        return self._package

    def __iter__(self):
        return iter(self.package.items('dkbuild'))

    def save(self):
        raise ValueError("No saving of dkbuild.ini")

    def _get(self, attr):
        return self.package.get('dkbuild', attr)

    def get(self, attr, default=None):
        try:
            return self._get(attr)
        except (KeyError, NoOptionError):
            return super(DkbuildIni, self).get(attr, default)

    def set(self, attr, val):
        self.package.set('dkbuild', attr, val)
