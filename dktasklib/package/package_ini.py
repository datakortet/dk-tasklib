# -*- coding: utf-8 -*-

"""Package based on package.ini
"""
from ConfigParser import RawConfigParser, NoOptionError
from dkfileutils.pfind import pfind
from .package_interface import PackageInterface


class PackageIni(PackageInterface):
    """Read package.ini::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """
    @classmethod
    def exists(cls):
        return pfind('.', 'package.ini') #or pfind('.', 'dkbuild.ini')

    def __init__(self, ctx=None, *args, **kw):
        super(PackageIni, self).__init__(
            ctx,
            fname=pfind('.', 'package.ini') #or pfind('.', 'dkbuild.ini')
        )
        self._package = None

    @property
    def package(self):
        if not self._package:
            self._package = RawConfigParser()
            self._package.read(self.fname)
        return self._package

    def __iter__(self):
        return iter(self.package.items('package'))

    def save(self):
        self.package.write(open(self.fname, 'w'))

    def _get(self, attr):
        return self.package.get('package', attr)

    def get(self, attr, default=None):
        try:
            return self._get(attr)
        except (KeyError, NoOptionError):
            return super(PackageIni, self).get(attr, default)

    def set(self, attr, val):
        self.package.set('package', attr, val)
