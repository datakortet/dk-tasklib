from dktasklib.wintask import task


@task
def clean(ctx, directory):
    """Remove all contents from build subdirectory `directory`.
    """
    ctx.run("rm -rf build/{directory}/*".format(directory=directory))
