import os
from threading import Lock

from nvimbols.content import Content, Wrapper, Highlight
from nvimbols.denite_content import DeniteContent
from nvimbols.util import log, on_error
from nvimbols.graph import Graph
from nvimbols.observable import Observable


def setup_nvimbols_help():
    content = Content()
    content += Highlight('Title', "NVimbols Help")
    content += "\nShortcuts:"
    content += Wrapper("\n ", Highlight('PreProc', "f"), ": Follow symbol")
    content += Wrapper("\n ", Highlight('PreProc', "v"), ": Follow symbol in split")
    content += Wrapper("\n ", Highlight('PreProc', "o"), ": Switch mode")
    content += Wrapper("\n ", Highlight('PreProc', "?"), ": Close help")
    content += "\n\nDefault keymappings:"
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sf"), ": Follow target")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sp"), ": Follow parent")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sb"), ": Follow base")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sF"), ": Follow target in split")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sP"), ": Follow parent in split")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sB"), ": Follow base in split")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sj"), ": Open Denite in symbol-mode")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sa"), ": Open Denite in list-mode")

    return content


class NVimbols(Observable):
    def __init__(self, parent, source, renderer):
        super().__init__()

        self._parent = parent
        self._source = source
        self._renderer = renderer
        self.filetypes = source.filetypes

        self._graph = Graph(self._source, self)
        self._current_location = None

        self._help_content = setup_nvimbols_help()

        """
        Pass notifications through
        """
        self._graph.on_update(lambda: self._notify())

        """
        'symbol': Display info about the symbol, the cursor is on
        'help': Display help
        'list': List symbols in file

        Implemented as stack
        """
        self._mode = ['symbol']

    def cancel(self):
        self._graph.cancel()

    def render(self):
        if self._mode[0] == 'help':
            return self._help_content
        else:
            return self._renderer.render(self._graph, self._current_location, self._mode[0])

    def render_denite(self, mode):
        return self._renderer.render_denite(self._graph, self._current_location, mode)

    def get_at_current_location(self):
        return self._graph.symbol(self._current_location)

    def update_location(self, location):
        self._current_location = location
        self._graph.request_at(location)
        self.render()

    def command(self, command):
        if command == 'clear':
            self._graph.clear()
            self.update_location(self._current_location)

        elif command == 'help':
            if self._mode[0] == 'help':
                del self._mode[0]
            else:
                self._mode = ['help'] + self._mode

        elif command == 'switch_mode':
            if self._mode[0] == 'help':
                return

            if self._mode[0] == 'symbol':
                self._mode = ['list'] + self._mode
            else:
                self._mode = ['symbol'] + self._mode

        self._notify()





