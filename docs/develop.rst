

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
One of::

    python setup.py test
    py.test dktasklib

with coverage::

    py.test --cov=dktasklib .


Building documentation
----------------------
::

    python setup.py build_sphinx

