# -*- coding: utf-8 -*-

"""Test that all modules are importable.
"""

import dktasklib._version
import dktasklib.clean
import dktasklib.executables
import dktasklib.jstools
import dktasklib.lessc
import dktasklib.manage
import dktasklib.npm
import dktasklib.package
import dktasklib.runners
import dktasklib.sysdeps
import dktasklib.version


def test_import_():
    "Test that all modules are importable."
    
    assert dktasklib._version
    assert dktasklib.clean
    assert dktasklib.executables
    assert dktasklib.jstools
    assert dktasklib.lessc
    assert dktasklib.manage
    assert dktasklib.npm
    assert dktasklib.package
    assert dktasklib.runners
    assert dktasklib.sysdeps
    assert dktasklib.version
