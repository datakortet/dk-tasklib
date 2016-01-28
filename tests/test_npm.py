# -*- coding: utf-8 -*-
# import subprocess

from dktasklib import npm
# from dktasklib.npm import cmd2args
# from dktasklib.utils import win32
from dktasklib.executables import exe


def test_installed():
    # print npm.npm('ls -g --depth=0 less')
    # print '\n\n\n\n'
    #
    # print subprocess.check_output(cmd2args('npm -ls -g --depth=0 less'), shell=win32).decode('u8')
    # print '\n\n\n\n'
    # for line in npm._run('npm -ls -g --depth=0 less'):
    #     print line
    assert exe.find('lessc', requires=['nodejs', 'npm'])
    assert npm.global_package('less')
    assert not npm.global_package('xyzxyxzs')
