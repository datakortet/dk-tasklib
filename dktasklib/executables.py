# -*- coding: utf-8 -*-
import sys
from dkfileutils.which import get_executable


class MissingCommand(Exception):
    """Exception thrown when a command (executable) is not found.
    """
    pass


class Executables(object):
    def __init__(self):
        self._cache = {}

    def require(self, *dependencies):
        """Ensure that all dependencies are available.
           You should not need to call this yourself, use the :fn:`requires`
           decorator instead.
        """
        for dep in dependencies:
            self.find(dep)

    def find(self, name, requires=(), install_txt='"'):
        if name not in self._cache:
            self.require(*requires)

            if hasattr(self, 'find_' + name):
                self._cache[name] = getattr(self, 'find_' + name)()
            else:
                self._cache[name] = self._find_exe(name, requires, install_txt)
        return self._cache[name]

    def _find_exe(self, name, requires=(), install_txt=None):
        fexe = get_executable(name)
        if not fexe:
            if install_txt is None:
                install_txt = "Missing command: %s %r" % (name, requires)
            raise MissingCommand(install_txt)
        return fexe

    def find_nodejs(self):
        if sys.platform == 'win32':
            node_exe = get_executable('node')
        else:
            node_exe = get_executable('nodejs') or get_executable('node')

        if not node_exe:
            raise MissingCommand("""
            Install Node.js using your OS package manager
            https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager
            """)
        return node_exe

    def find_npm(self):
        npm_exe = get_executable('npm')
        if not npm_exe:
            raise MissingCommand("""
            Install Node.js using your OS package manager
            https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager
            """)
        return npm_exe


#: public interface to the Executables class
exe = Executables()


def requires(*deps):
    """Decorator to declare global dependencies/requirements.

       Usage (``@task`` must be last)::

           @requires('nodejs', 'npm', 'lessc')
           @task
           def mytask(..)

    """
    def _wrapper(fn):
        exe.require(*deps)
        def _inner(*args, **kwargs):
            return fn(*args, **kwargs)
        return _inner
    return _wrapper




