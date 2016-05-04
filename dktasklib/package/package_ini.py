# -*- coding: utf-8 -*-

"""Package based on package.ini or dkbuild.ini
"""
from ConfigParser import RawConfigParser, NoOptionError
from dkfileutils.pfind import pfind
from .package_interface import PackageInterface


class IniPackageFile(PackageInterface):
    """Read package.ini::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """
    INI_NAME = ""

    @classmethod
    def exists(cls):
        return pfind('.', cls.INI_NAME + '.ini')

    def __init__(self, ctx=None, *args, **kw):
        super(IniPackageFile, self).__init__(
            ctx,
            fname=pfind('.', self.INI_NAME + '.ini')
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

    def get(self, attr, default=None):
        try:
            return self.package.get('package', attr)
        except (KeyError, NoOptionError):
            return super(IniPackageFile, self).get(attr, default)

    def set(self, attr, val):
        self.package.set('package', attr, val)


class PackageIni(IniPackageFile):
    INI_NAME = 'package'


class DkBuildIni(IniPackageFile):
    INI_NAME = 'dkbuild'
