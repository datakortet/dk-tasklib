# -*- coding: utf-8 -*-
from __future__ import print_function
import subprocess


class Result(str):
    cmd = None
    returncode = None


def run(cmdline, throw=False):
    try:
        output = subprocess.check_output(cmdline, shell=True)
        res = Result(output.decode('u8'))
        res.cmd = cmdline
        return res
    except subprocess.CalledProcessError as e:
        if throw:
            raise
        output = e.output.decode('u8') if isinstance(e.output, bytes) else e.output
        res = Result(output)
        res.cmd = cmdline
        res.returncode = e.returncode
        return res


def command(executable, dryrun=False):
    def _call(*args, **kwargs):
        cmdline = " ".join(args)
        for k, v in kwargs.items():
            if v is True:
                cmdline += " --" + k
            else:
                if ' ' in v:
                    v = '"%s"' % v
                cmdline += ' --%s=%s' % (k, v)

        if dryrun:
            print(cmdline)
        else:
            return run(cmdline)
    return _call
