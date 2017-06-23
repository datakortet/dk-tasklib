# -*- coding: utf-8 -*-

"""Package based on setup.py
"""
from dkfileutils.pfind import pfind
from .package_interface import PackageInterface


class SetupPy(PackageInterface):
    """Read setup.py file::

           pkg = dktasklib.Package()
           VERSION = pkg.version

    """

    @classmethod
    def exists(cls):
        return pfind('.', 'setup.py')

    def __init__(self, ctx=None, *args, **kw):
        super(SetupPy, self).__init__(
            ctx,
            fname=pfind('.', 'setup.py')
        )
        self._package = None

    def save(self):
        return

    def __iter__(self):
        return iter([])

    def _get(self, attr):
        if attr == 'version':
            with self.root.cd():
                return self.ctx.run('python setup.py --version',
                                    hide=True).stdout.strip()
        raise AttributeError(attr)

    def get(self, key, default=None):
        try:
            return self._get(key)
        except AttributeError:
            return super(SetupPy, self).get(key, default)

    def set(self, attr, val):
        raise KeyError("Cannot set values in the setup.py file")
