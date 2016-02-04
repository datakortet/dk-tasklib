# -*- coding: utf-8 -*-

from .setup_file import SetupPy
from .package_ini import PackageIni
from .package_json import PackageJson


def Package(*args, **kwargs):
    import os

    # these are listed in order of preference
    if PackageIni.exists():
        return PackageIni(*args, **kwargs)
    elif PackageJson.exists():
        return PackageJson(*args, **kwargs)
    elif SetupPy.exists():
        return SetupPy(*args, **kwargs)
    else:
        raise RuntimeError("""
        Looked for package starting from {cwd}, but couldn't find any of:

         - package.ini
         - dkbuild.ini
         - package.json
         - setup.py

        Please create one of them in the root directory of your package.
        """.format(cwd=os.getcwd()))
