import neovim
import json
from subprocess import Popen, PIPE


def on_error(err):
    with open('/tmp/pylog', 'w') as log:
        log.write(str(err))
    raise err


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim


    @neovim.function('_nvimbols_update_location')
    def reindex_unsaved(self, args):
        buf = self.vim.current.buffer
        filename = buf.name
        on_error(args)










