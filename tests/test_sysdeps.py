# -*- coding: utf-8 -*-


from dktasklib.sysdeps import have_npm, have_nodejs, have_lessc


def test_have_nodejs(ctx):
    assert have_nodejs(ctx)


def test_have_npm(ctx):
    assert have_npm(ctx)


def test_have_lessc(ctx):
    assert have_lessc(ctx)
