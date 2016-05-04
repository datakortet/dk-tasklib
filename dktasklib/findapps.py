# -*- coding: utf-8 -*-

"""Module for finding all apps folders.
"""

import os
from dkfileutils.path import Path


def is_appfolder(path):
    """Is the ``path`` an app folder?
    """
    path = Path(path)
    if path.isdir():
        if (path / 'urls.py').exists():
            return True

        if (path / 'models.py').exists():
            return True

        if (path / 'models').exists():
            return True

    return False


def appname(folder):
    """Return the app name for the (app)folder.
    """
    _, app = os.path.split(folder)
    return app
