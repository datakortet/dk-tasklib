import subprocess

from dktasklib.executables import exe


def npm(cmdline):
    npm_exe = exe.find('npm', requires=['nodejs'])      # noqa
    return subprocess.check_output("npm " + cmdline, shell=True).decode('u8')


def global_package(pkgname):
    """Check if an npm package is installed globally.
    """
    try:
        # this is the 'correct' way, but it's increadably slow (4+ secs)
        npm('ls -g --depth 0 ' + pkgname)
        return True
    except subprocess.CalledProcessError:
        return False
