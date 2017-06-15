# -*- coding: utf-8 -*-
import pprint
import invoke
from dkfileutils.path import Path
from dkfileutils.changed import Directory
from invoke.config import Config


class PackageInterface(object):
    fallback_modules = []

    def __init__(self, ctx=None, fname=None):
        self._args = ()
        self._kwargs = dict(ctx=ctx, fname=fname)

        self.ctx = ctx or invoke.Context()
        self.fname = fname

    @property
    def root(self):
        return Path(self.fname).dirname()

    @property
    def package_name(self):
        return self.root.split()[1]

    @property
    def name(self):
        return self.package_name.replace('-', '')

    @property
    def sourcedir(self):
        """Return the root of this package's source tree.
        """
        is_package = 'setup.py' in self.root
        return Directory((self.root / self.name) if is_package else self.root)

    @property
    def docsdir(self):
        """Return the root of this package's documentation tree.
        """
        return Directory(self.get('docsdir', self.root / 'docs'))

    @property
    def staticdir(self):
        """Return the root of this package's static tree.
        """
        is_package = 'setup.py' in self.root
        return Directory((self.root / self.name / 'static')
                         if is_package else self.root / 'static')

    def config(self):  # pragma: nocover
        cfg = Config(dict(iter(self)))
        cfg.name = self.name
        cfg.root = self.root
        cfg.sourcedir = self.sourcedir
        cfg.docsdir = self.docsdir
        cfg.staticdir = self.staticdir
        return cfg

    def __repr__(self):
        return self.__class__.__name__
        # return pprint.pformat(self.config())

    def __getattr__(self, item):
        # for convenience (continue using [](__setitem__) for setting).
        if item.startswith('_'):
            raise AttributeError(item)
        return self.get(item)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        result = self.set(key, value)
        self.save()
        return result

    # maybe override next methods

    def set_version(self, version):
        # override this for special handling of versions
        return self.set('version', version)

    # must override next methods

    def save(self):
        """Save the package config file with current values.
        """
        raise NotImplementedError

    def __iter__(self):
        return iter([])

    def get(self, attr, default=None):
        """Override this method, and call super if the attribute is not found::

            def get(self, attr, default=None):
                try:
                    return ...
                except ...:
                    return super(SubClass, self).get(attr, default)

        """
        for backend in self.__class__.fallback_modules:
            m = backend(*self._args, **self._kwargs)
            try:
                # print 'dkinterface-get:', attr, 'backend:', m.__class__.__name__
                return m._get(attr)
            except AttributeError:
                pass

        if default is not None:
            return default
        raise AttributeError(
            self.fname + " does not have an attribute named: " + attr
        )

    def set(self, key, value):  # pragma: nocover
        raise NotImplementedError
