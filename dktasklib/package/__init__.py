# -*- coding: utf-8 -*-
from invoke import ctask as task

from .setup_file import SetupPy
from .package_ini import PackageIni
from .dkbuild_ini import DkbuildIni
from .package_json import PackageJson


def Package(*args, **kwargs):
    import os

    # these are listed in order of preference
    if DkbuildIni.exists():
        return DkbuildIni(*args, **kwargs)
    elif PackageIni.exists():
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


@task
def package(ctx):
    """Print detected package directories.
    """
    pkg = Package()
    keys = ['package_name', 'name', 'fname', 'root', 'source',
            'docs', 'django_static']
    keylen = 1 + max(len(k) for k in keys)
    vallen = 1 + max(len(str(getattr(pkg, k))) for k in keys)
    print "The dk-tasklib Package object thinks your code has the following layout:"
    print
    print '-' * keylen, '-' * vallen, '-' * (80 - keylen - vallen)
    print 'attribute'.ljust(keylen), 'value'.ljust(vallen), 'description'
    print '-' * keylen, '-' * vallen, '-' * (80 - keylen - vallen)

    print 'package_name'.ljust(keylen), str(pkg.package_name).ljust(vallen), '(repo name)'
    print 'name'.ljust(keylen), str(pkg.name).ljust(vallen), '(importable name)'
    print 'fname'.ljust(keylen), str(pkg.fname).ljust(vallen), '(name of file providing package info)'
    print 'root'.ljust(keylen), str(pkg.root).ljust(vallen), '(root of the package/wc)'
    print 'source'.ljust(keylen), str(pkg.source).ljust(vallen), '(root of the source code)'
    print 'docs'.ljust(keylen), str(pkg.docs).ljust(vallen), '(root of documentation)'
    print 'django_static'.ljust(keylen), str(pkg.django_static).ljust(vallen), '(directory for static resources)'

    print '-' * keylen, '-' * vallen, '-' * (80 - keylen - vallen)
