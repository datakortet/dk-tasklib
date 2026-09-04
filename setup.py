#!/usr/bin/env python

"""dk-tasklib - pyinvoke task library
"""
import os
import sys
import setuptools

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Topic :: Software Development :: Libraries
"""

version = '3.0.9'
DIRNAME = os.path.dirname(__file__)


setuptools.setup(
    name='dk-tasklib',
    version=version,
    install_requires=[
        "invoke",
        "PyYAML",
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
