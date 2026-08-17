

Developing dktasklib
====================


Uploading to PyPI
-----------------

- only source distribution::

    python setup.py sdist upload

- source and windows installer::

    python setup.py sdist bdist_wininst upload

- source, windows, and wheel installer::

    python setup.py sdist bdist_wininst bdist_wheel upload

- create a documentation bundle to upload to PyPi::

    python setup.py build_sphinx
    python setup.py upload_docs


.. note:: if you're using this as a template for new projects, remember to
          `python setup.py register <projectname>` before you upload to
          PyPi.


Running tests
-------------
Run the package-specific environment, tests, coverage, and quality checks::

    dk testpackage

The configured coverage gate is branch-aware and requires at least 83
percent combined coverage.


Building documentation
----------------------
::

    dk docs

For strict compatibility checks, the documentation also builds without
warnings under supported Sphinx 8 and 9 environments::

    sphinx-build -E -W -b html docs build/docs
