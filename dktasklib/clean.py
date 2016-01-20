# -*- coding: utf-8 -*-

from invoke import task, run


@task
def clean_less():
    "Clean less build area."
    run("rm -rf build/less")
    run("mkdir -p build/less")


@task
def clean_js():
    "Clean js build area."
    run("rm -rf build/js")
    run("mkdir -p build/js")


@task
def clean():
    "Clean build area."
    run("rm -rf build")
    run("mkdir build")
