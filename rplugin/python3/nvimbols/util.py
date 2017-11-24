"""

This file is pretty much copied from Shougo/deoplete

"""

import os
import glob
import sys
import traceback

from importlib.machinery import SourceFileLoader


def find_rplugins(rtp):
    """
    Search for *.py in VIMRUNTIME/*/rplugin/python3/nvimbols/sources/
    """
    rtp = rtp.split(',')
    if not rtp:
        return

    for src in ['rplugin/python3/nvimbols/sources/*.py', 'rplugin/python3/nvimbols/sources/**/*.py']:
        for path in rtp:
            yield from glob.iglob(os.path.join(path, src))


def import_plugin(path, source, classname):
    """
    Import NVimbols source class if the class exists, add its directory to sys.path.
    """
    name = os.path.splitext(os.path.basename(path))[0]
    module_name = 'nvimbols.%s.%s' % (source, name)

    module = SourceFileLoader(module_name, path).load_module()
    cls = getattr(module, classname, None)
    if not cls:
        return None

    dirname = os.path.dirname(path)
    if dirname not in sys.path:
        sys.path.insert(0, dirname)
    return cls


def error(vim, expr):
    if vim is not None:
        vim.session.threadsafe_call(lambda: vim.command("echom(\"[nvimbols] %s \")" % str(expr).replace("\"", "\\\"")))
    log("[error] %s" % str(expr))


def on_error(vim, err):
    for line in traceback.format_exc().splitlines():
        error(vim, str(line))
    error(vim, '%s.  Use :messages for error details.' % str(err))


def on_error_wrap(vim, func):
    def wrapped():
        try:
            func()
        except Exception as err:
            on_error(vim, err)
    return wrapped


def log(msg):
    with open('/tmp/pylog', 'a') as f:
        f.write(str(msg) + "\n")

