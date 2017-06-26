# -*- coding: utf-8 -*-

"""Test that all modules are importable.
"""

import dktasklib._version
import dktasklib.clean
import dktasklib.commands
import dktasklib.concat
import dktasklib.environment
import dktasklib.executables
import dktasklib.help
import dktasklib.jstools
import dktasklib.lessc
import dktasklib.manage
import dktasklib.npm
import dktasklib.package
# import dktasklib.package.package_ini
import dktasklib.package.package_interface
# import dktasklib.package.package_json
# import dktasklib.package.setup_file
import dktasklib.pset
import dktasklib.publish
import dktasklib.rule
import dktasklib.runners
import dktasklib.urlinliner
import dktasklib.version


def test_import_():
    """Test that all modules are importable.
    """
    
    assert dktasklib._version
    assert dktasklib.clean
    assert dktasklib.commands
    assert dktasklib.concat
    assert dktasklib.environment
    assert dktasklib.executables
    assert dktasklib.help
    assert dktasklib.jstools
    assert dktasklib.lessc
    assert dktasklib.manage
    assert dktasklib.npm
    assert dktasklib.package
    # assert dktasklib.package.package_ini
    assert dktasklib.package.package_interface
    # assert dktasklib.package.package_json
    # assert dktasklib.package.setup_file
    assert dktasklib.pset
    assert dktasklib.publish
    assert dktasklib.rule
    assert dktasklib.runners
    assert dktasklib.urlinliner
    assert dktasklib.version
