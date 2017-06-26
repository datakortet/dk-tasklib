# -*- coding: utf-8 -*-
import os

from dktasklib.wintask import task
from dktasklib.wintask import task


@task
def clean(ctx, directory):
    """Remove all contents from build subdirectory `directory`.
    """
    # ctx.run("rm -rf build/{directory}/*".format(directory=directory), shell=os.environ['COMSPEC'])
    ctx.run("rm -rf build/{directory}/*".format(directory=directory))
