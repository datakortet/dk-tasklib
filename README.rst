
.. image:: https://travis-ci.org/datakortet/dk-tasklib.svg?branch=master
   :target: https://travis-ci.org/datakortet/dk-tasklib

.. image:: https://coveralls.io/repos/github/datakortet/dk-tasklib/badge.svg?branch=master
   :target: https://coveralls.io/github/datakortet/dk-tasklib?branch=master

dk-tasklib - pyinvoke task library
====================================


Installing from PyPI
--------------------

This is what you want if you just want to use dk-tasklib:

   pip install dk-tasklib


Creating a default tasks.py file
--------------------------------
You can create a default ``tasks.py`` file. From the root of your package::

    dk-tasklib install

You'll need to specify ``--force`` to overwrite an existing file.

As a source package
-------------------
This is what you want if you are developing dk-tasklib or want 
to make local changes to the source code.

   pip install -e <path>


See docs/ folder for documentation.


Development
-----------

Run the authoritative package checks from the repository root::

    dk testpackage

The suite enforces branch-aware coverage of at least 83 percent. Build the
documentation with::

    dk docs

The documentation is maintained against current Sphinx 8 and 9 releases.
