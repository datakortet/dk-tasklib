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
    def root(self):  # ok
        return Path(self.fname).dirname()

    @property
    def package_name(self): # ok
        return self.root.split()[1]

    @property
    def name(self):  # ok
        return self.package_name.replace('-', '')

    @property
    def source(self):  # source
        """Return the root of this package's source tree.
        """
        is_package = 'setup.py' in self.root
        return Directory((self.root / self.name) if is_package else self.root)

    @property
    def docsdir(self):  # -> docs
        """Return the root of this package's documentation tree.
        """
        try:
            return Directory(self.get('docsdir'))
        except KeyError:
            return Directory(self.root / 'docs')

    @property
    def staticdir(self):  # staticdir -> django_static
        """Return the root of this package's static tree.
        """
        is_package = 'setup.py' in self.root
        return Directory((self.root / self.name / 'static')
                         if is_package else self.root / 'static')

    # invoke'ism?
    def config(self):  # pragma: nocover
        cfg = Config(dict(iter(self)))
        cfg.name = self.name
        cfg.root = self.root
        cfg.sourcedir = self.source
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

    # must override next methods

    # save is a bad idea!
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
            except (AttributeError, KeyError):
                pass

        if default is not None:
            return default

        raise AttributeError(
            self.fname + " does not have an attribute named: " + attr
        )

    def set(self, key, value):  # pragma: nocover
        raise NotImplementedError
