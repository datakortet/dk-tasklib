# -*- coding: utf-8 -*-

from invoke import ctask as task


@task
def clean(ctx, directory):
    """Remove all contents from build subdirectory `directory`.
    """
    ctx.run("rm -rf build/{directory}/*")


# @task
# def clean_less():
#     "Clean less build area."
#     run("rm -rf build/less")
#     run("mkdir -p build/less")
#
#
# @task
# def clean_js():
#     "Clean js build area."
#     run("rm -rf build/js")
#     run("mkdir -p build/js")
#
#
# @task
# def clean():
#     "Clean build area."
#     run("rm -rf build")
#     run("mkdir build")
