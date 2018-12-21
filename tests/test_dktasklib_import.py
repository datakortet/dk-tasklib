# -*- coding: utf-8 -*-

"""Test that all modules are importable.
"""

import dktasklib._version
import dktasklib.clean
import dktasklib.commands
import dktasklib.concat
import dktasklib.entry_points
import dktasklib.entry_points.confbase
import dktasklib.entry_points.dktasklibcmd
import dktasklib.entry_points.pytemplate
import dktasklib.entry_points.taskbase
import dktasklib.environment
import dktasklib.executables
import dktasklib.help
import dktasklib.jstools
import dktasklib.lessc
import dktasklib.manage
import dktasklib.npm
import dktasklib.package
import dktasklib.package.package_interface
import dktasklib.pset
import dktasklib.publish
import dktasklib.rule
import dktasklib.runners
import dktasklib.upversion
import dktasklib.urlinliner
import dktasklib.version
import dktasklib.watch
import dktasklib.wintask


def test_import_():
    "Test that all modules are importable."
    
    assert dktasklib._version
    assert dktasklib.clean
    assert dktasklib.commands
    assert dktasklib.concat
    assert dktasklib.entry_points
    assert dktasklib.entry_points.confbase
    assert dktasklib.entry_points.dktasklibcmd
    assert dktasklib.entry_points.pytemplate
    assert dktasklib.entry_points.taskbase
    assert dktasklib.environment
    assert dktasklib.executables
    assert dktasklib.help
    assert dktasklib.jstools
    assert dktasklib.lessc
    assert dktasklib.manage
    assert dktasklib.npm
    assert dktasklib.package
    assert dktasklib.package.package_interface
    assert dktasklib.pset
    assert dktasklib.publish
    assert dktasklib.rule
    assert dktasklib.runners
    assert dktasklib.upversion
    assert dktasklib.urlinliner
    assert dktasklib.version
    assert dktasklib.watch
    assert dktasklib.wintask
