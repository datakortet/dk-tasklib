# -*- coding: utf-8 -*-
from dktasklib.wintask import task
from .package_interface import Package


@task
def package(ctx):
    """Print detected package directories.
    """
    pkg = Package()
    keys = ['package_name', 'name', 'fname', 'root', 'source',
            'docs', 'django_static']
    keylen = 1 + max(len(k) for k in keys)
    vallen = 1 + max(len(str(getattr(pkg, k, ''))) for k in keys)
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
