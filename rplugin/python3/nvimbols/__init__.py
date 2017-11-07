import neovim
import os
import time

from nvimbols.util import find_rplugins, import_plugin, on_error, log
from nvimbols.nvimbols import NVimbols
from nvimbols.symbol import SymbolLocation


@neovim.plugin
class NVimbolsPlugin(object):
    def __init__(self, vim):
        self._vim = vim
        self._main = None
        self._sources = None

    @neovim.function('_nvimbols_init')
    def init(self, args):
        log('[INIT START]')
        context = args[0]

        if(self._sources is None):
            self._sources = {}

            for path in find_rplugins(context['rtp']):
                name = os.path.splitext(os.path.basename(path))[0]
                source = None
                try:
                    Source = import_plugin(path, 'source', 'Source')
                    if not Source:
                        continue

                    source = Source(self._vim)
                    source.name = getattr(source, 'name', name)
                    source.path = path

                    log('SOURCE: %s' % source.name)

                    self._sources[source.name] = source

                except Exception as err:
                    on_error(self._vim, err)

        ft = context['ft']
        possible_sources = []
        for s in self._sources:
            if(ft in self._sources[s].supported_filetypes()):
                possible_sources += [self._sources[s]]

        selected_source = None
        if(len(possible_sources) != 0):
            selected_source = possible_sources[0]

        if(selected_source is not None):
            self._main = NVimbols(self._vim, context, selected_source)
        else:
            self._main = None

    @neovim.function('_nvimbols_update_location')
    def update_location(self, args):
        if(self._main is None):
            return

        log('[UPDATE_LOCATION]')

        try:
            buf = self._vim.current.buffer
            filename = buf.name
            line = args[0]
            col = args[1]

            location = SymbolLocation(filename, line, col)
            self._main.update_location(location)

        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_nvimbols_render')
    def render(self, args):
        if(self._main is None):
            return

        log('[RENDER]')

        try:
            window_number = args[0]['window_number']
            buf = self._vim.windows[window_number - 1].buffer
            self._main.render(buf)
        except Exception as err:
            on_error(self._vim, err)

    @neovim.function('_nvimbols_get_link', sync=True)
    def get_link(self, args):
        try:
            line = args[0]
            col = args[1]

            return self._main.get_link(line, col)
        except Exception as err:
            on_error(self._vim, err)
















