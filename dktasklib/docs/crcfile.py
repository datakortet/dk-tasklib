# -*- coding: utf-8 -*-
import os
import textwrap
import zlib


class CRCFile(file):
    """A file that ends with `\n..crc:___` where `___` is the `zlib.crc32()`
       of the file contents up to that point.  If the file contents does not
       correspond to the crc32 the file cannot be opened by this class.
    """
    def _get_crc_can_open(self, fname):
        if not os.path.exists(fname):
            return True
        with open(fname) as fp:
            txt = fp.read()
        if '\n.. crc:' not in txt:
            return True
        txt, crc = txt.split('\n.. crc:')
        if int(crc, 10) == zlib.crc32(txt):
            return True
        return False

    def __init__(self, name):
        if not self._get_crc_can_open(name):
            raise RuntimeError(
                "File %r has been changed, exiting "
                "(remove crc line to overwrite)." % name)
        self._output = ""
        super(CRCFile, self).__init__(name, 'w')

    def close(self):
        self.write('\n.. crc:%d' % zlib.crc32(self._output))
        return super(CRCFile, self).close()

    def write(self, *args, **kw):
        txt = ' '.join(str(arg) for arg in args)
        # tmp = {}
        # tmp.update(self.__dict__)
        # tmp.update(kw)
        output = textwrap.dedent(txt)
        self._output += output
        super(CRCFile, self).write(output)
