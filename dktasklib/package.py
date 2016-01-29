# -*- coding: utf-8 -*-

import json
import os
import invoke
from invoke.config import Config

from ConfigParser import RawConfigParser, NoOptionError
from dkfileutils.pfind import pfind


class PackageInterface(object):
    def __init__(self, ctx=None, fname=None):
        self.ctx = ctx or invoke.Context()
        self.fname = fname

    @property
    def root(self):
        return os.path.dirname(self.fname)

    def upversion(self, major=False, minor=False, patch=False):
        """Update package version (default patch-level increase).
        """
        if not (major or minor or patch):
            # this is normally set by version.upversion
            patch = True  # pragma: nocover
        version = [int(n, 10) for n in self.version.split('.')]
        if major:
            version[0] += 1
        if minor:
            version[1] += 1
        if patch:
            version[2] += 1
        newversion = '.'.join([str(n) for n in version])
        self.set_version(newversion)
        return newversion

    def set_version(self, version):
        # override this for special handling of versions
        self['version'] = newversion

    def get_config(self):
        # override to provide config values from file.
        return Config()

    def config(self):  # pragma: nocover
        cfg = self.get_config()
        cfg.root = self.root
        return cfg

    # for convenience (continue using [](__setitem__) for setting).
    def __getattr__(self, item):
        return self[item]

    def __setitem__(self, key, value):  # pragma: nocover
        # should override
        pass

    def __getitem__(self, item, default=None):  # pragma: nocover
        # should override
        return ''

    def get(self, key, default=None):
        return self.__getitem__(key, default)


class PackageIni(PackageInterface):
    """Read package.ini or dkbuild.ini file::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """
    @classmethod
    def exists(cls):
        return pfind('.', 'package.ini') or pfind('.', 'dkbuild.ini')

    def __init__(self, ctx=None, *args, **kw):
        super(PackageIni, self).__init__(
            ctx,
            fname=pfind('.', 'package.ini') or pfind('.', 'dkbuild.ini')
        )
        if self.fname is None:  # pragma: nocover
            raise RuntimeError("""
                I couldn't find a package.json, package.ini,
                or dkbuild.ini file starting from %s.
                """ % os.getcwd())
        self._package = None

    def _open(self, fname):
        self._package = RawConfigParser()
        self._package.read(self.fname)

    @property
    def package(self):
        if not self._package:
            self._open(self.fname)
        return self._package

    def __setitem__(self, attr, val):
        self.package.set('package', attr, val)
        self.package.write(open(self.fname, 'w'))

    def get_config(self):
        return Config(dict(self.package.items('package')))

    def __getitem__(self, attr, default=None):
        try:
            return self.package.get('package', attr)
        except (KeyError, NoOptionError):
            # return default
            if default is not None:
                return default
            raise AttributeError(
                self.fname + " does not have an attribute named: " + attr)


class PackageJson(PackageInterface):
    """Read package.json file::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """
    @classmethod
    def exists(cls):
        return pfind('.', 'package.json')

    def __init__(self, ctx=None, basedir=None, packagejson='package.json'):
        if basedir:
            fname = os.path.join(basedir, packagejson)
        else:
            fname = pfind('.', packagejson)

        super(PackageJson, self).__init__(ctx, fname=fname)

        if basedir is None:
            if self.fname is None:  # pragma: nocover
                raise RuntimeError("I couldn't find a %s file" % packagejson)

        self._package = None

    @property
    def package(self):
        if not self._package:
            with open(self.fname) as fp:
                self._package = json.loads(fp.read())
        return self._package

    def __setitem__(self, key, value):
        self.package[key] = value
        json.dump(self.package, open(self.fname, 'w'), indent=4)

    def get_config(self):
        return Config(self.package)

    def __getitem__(self, attr, default=None):
        try:
            return self.package[attr]
        except KeyError:
            # return default
            if default is not None:
                return default
            raise AttributeError(
                self.fname + " does not have an attribute named: " + attr)


def Package(*args, **kwargs):
    if PackageJson.exists():
        return PackageJson(*args, **kwargs)
    else:
        return PackageIni(*args, **kwargs)

