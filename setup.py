#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dk-tasklib - pyinvoke task library
"""
import os
import sys
import setuptools

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Topic :: Software Development :: Libraries
"""

version = '3.0.0'
DIRNAME = os.path.dirname(__file__)


setuptools.setup(
    name='dk-tasklib',
    version=version,
    install_requires=[
        "invoke==1.2.0",
        "PyYAML==5.1.2",
        "dkfileutils>=1.4.2",
        "yamldirs>=1.1.8",
    ],
    author='Bjorn Pettersen',
    author_email='bp@datakortet.no',
    url='https://github.com/datakortet/dk-tasklib',
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': """
            dk-tasklib = dktasklib.entry_points.dktasklibcmd:main
        """
    },
    zip_safe=False,
)
