# -*- coding: utf-8 -*-
"""Check if contents of directory has changed.
"""
import sys
import argparse
import inspect
from dkfileutils.changed import changed


class changed_dir(object):
    """Has `glob` changed in `dirname` or `force`
    """

    class NoChange(ValueError):
        pass

    def __init__(self,
                 dirname,
                 glob='**/*',
                 filename='.md5',
                 force=False,
                 msg="nothing to do"):
        self.dirname = dirname
        self.glob = glob
        self.filename = filename
        self.force = force
        self.msg = msg
        self._trace = None

    def __enter__(self):
        if self.force or changed(self.dirname, self.glob, self.filename):
            return
        else:
            print self.msg
            # this horrid hack is just barely ok in task.py code...
            # (expect debuggers/pylint/coverage/etc. to be unhappy)
            self._trace = sys.gettrace()
            sys.settrace(lambda *args, **kw: None)
            frame = inspect.currentframe(1)
            # set the trace function below on parent frame
            frame.f_trace = self.trace

    def trace(self, frame, event, arg):
        # we just entered the with block.. cleanup and exit immediately
        sys.settrace(self._trace)
        raise changed_dir.NoChange()

    def __exit__(self, type, value, traceback):
        return isinstance(value, changed_dir.NoChange)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        'directory',
        help="Directory to check"
    )
    p.add_argument(
        '--verbose', '-v', action='store_true',
        help="increase verbosity"
    )
    args = p.parse_args()

    import sys, time

    start = time.time()
    _changed = changed(sys.argv[1], args=args)
    # print 'done:', time.time() - start
    sys.exit(_changed)
