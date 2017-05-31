# -*- coding: utf-8 -*-

"""Package based on dkbuild.ini
"""
from ConfigParser import NoOptionError, RawConfigParser

from dkfileutils.pfind import pfind

from .package_interface import PackageInterface


class DkbuildIni(PackageInterface):
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
        print 4
        return iter(self.package.items('dkbuild'))

    def save(self):
        print 4
        pass

    def __getstate__(self):
        res = {k: self[k] for k in self.package.options('dkbuild')}
        print "GETSTATE:", res
        return res

    # def __getattr__(self, item):
    #     print "GETattr:", item
    #     if item.startswith('_'):
    #         raise AttributeError(item)
    #     try:
    #         return self.package.get('dkbuild', item)
    #     except (KeyError, NoOptionError):
    #         raise AttributeError(item)

    def get(self, attr, default=None):
        print "GET:", attr, default
        print 4
        return self.package.get('dkbuild', attr)
        # try:
        #     return self.package.get('dkbuild', attr)
        # except (KeyError, NoOptionError):
        #     return super(DkbuildIni, self).get(attr, default)

    def set(self, attr, val):
        self.package.set('dkbuild', attr, val)
