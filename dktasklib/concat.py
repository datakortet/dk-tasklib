import os
import sys

from dkfileutils.path import Path


def line_endings(fname):
    """Return all line endings in the file.
    """
    _endings = {line[-2:] for line in open(fname, 'rb').readlines()}
    res = set()
    for e in _endings:
        if e.endswith(b'\r'):
            res.add(b'\r')
        elif e.endswith(b'\r\n'):
            res.add(b'\r\n')
        elif e.endswith(b'\n'):
            res.add(b'\n')
    return res


def chomp(s):
    """Remove line terminator if it exists.
    """
    if s[-2:] == b'\r\n':
        return s[:-2]
    if s[-1:] == b'\r' or s[-1:] == b'\n':
        return s[:-1]
    return s


def fix_line_endings(fname, eol=b'\n'):
    """Change all line endings to ``eol``.
    """
    lines = [chomp(line) for line in open(fname, 'rb').readlines()]
    with open(fname, 'wb') as fp:
        for line in lines:
            fp.write(line + eol)


def copy(ctx, source, dest, force=False):
    """Copy ``source`` to ``dest``, which can be a file or directory.
    """
    if source == dest:
        return dest

    source = os.path.normcase(os.path.normpath(str(source)))
    dest = os.path.normcase(os.path.normpath(str(dest)))
    flags = ""
    if sys.platform == 'win32':
        if force:
            flags += " /Y"
        ctx.run('copy {flags} {source} {dest}'.format(**locals()))
    else:  # pragma: nocover
        if force:
            flags += " --force"
        ctx.run('cp {flags} {source} {dest}'.format(**locals()))
    return dest


def concat(ctx, dest, *sources, **kw):
    force = kw.pop('force', False)      # noqa
    placement = Path(dest).dirname()
    placement.makedirs()

    with open(dest, 'w') as out:
        print("Opened:", dest, "for writing.")
        for s in sources:
            with open(s, 'r') as inp:
                print("  appending:", s)
                out.writelines(inp.readlines())
        out.write('\n')

    fix_line_endings(dest)

    return dest
