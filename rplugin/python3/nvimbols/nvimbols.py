import os

from nvimbols.content import Content, Wrapper, Highlight
from nvimbols.util import log, on_error
from nvimbols.graph import SymbolsGraph

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
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sj"), ": Open Denite")

    return content

class NVimbols:
    def __init__(self, parent, source):
        self._parent = parent
        self._source = source
        self.filetypes = source.filetypes
        self._graph = SymbolsGraph(self._source, self)

        self._current_location = None
        self._current_content = None

        self._help_content = setup_nvimbols_help()

        """
        'symbol': Display info about the symbol, the cursor is on
        'help': Display help
        'list': List symbols in file

        Implemented as stack
        """
        self._mode = ['symbol']

    def render(self, force_put=False):
        content = Content()
        if self._mode[0] == 'symbol':
            content = self._source.render_location(self._graph.get_location(self._current_location))
        elif self._mode[0] == 'help':
            content = self._help_content
        elif self._mode[0] == 'list':
            # TODO
            content = Content()

        if force_put or self._current_content != content:
            self._parent.put_content(content)
        self._current_content = content

    def get_current_location(self):
        return self._graph.get_location(self._current_location)

    def update_location(self, location):
        self._current_location = location
        self._graph.require_symbol(location)
        self.render()

    def get_link(self, line, col):
        if(self._current_content is None):
            return ""

        for link in self._current_content.links():
            if(link.line == line and link.start_col <= col and (link.end_col == -1 or link.end_col >= col)):
                return str(link.target)

        return ""

    def get_first_reference(self, reference_name):
        location = self._graph.get_location(self._current_location)
        if(location is None or location.symbol.is_loading()):
            return ""

        symbol = location.symbol.get()
        if(symbol is None):
            return ""

        for r in self._graph.references:
            if r.name == reference_name:
                log(str(symbol.get_source_of(r)[0]) if len(symbol.get_source_of(r)) > 0 else "")
                return str(symbol.get_source_of(r)[0]) if len(symbol.get_source_of(r)) > 0 else ""

        return ""

    def command(self, command):
        if command == 'clear':
            self._graph.clear()
            self.update_location(self._current_location)
        elif command == 'help':
            if self._mode[0] == 'help':
                del self._mode[0]
            else:
                self._mode = ['help'] + self._mode

            self.render(True)
        elif command == 'switch_mode':
            if self._mode[0] == 'help':
                return

            if self._mode[0] == 'symbol':
                self._mode = ['list'] + self._mode
            else:
                self._mode = ['symbol'] + self._mode

            self.render(True)




