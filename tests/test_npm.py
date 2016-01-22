# -*- coding: utf-8 -*-

from dktasklib import npm


def test_installed(ctx):
    assert npm.is_installed(ctx, 'lessc')
