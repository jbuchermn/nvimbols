import os
from threading import Lock

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
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sj"), ": Open Denite in symbol-mode")
    content += Wrapper("\n ", Highlight('PreProc', "<leader>sa"), ": Open Denite in list-mode")

    return content


class NVimbols:
    def __init__(self, parent, source):
        self._parent = parent
        self._source = source
        self.filetypes = source.filetypes

        self._graph = SymbolsGraph(self._source, self)
        self._source.set_graph(self._graph)

        """
        Rerender at every change in graph
        """
        self._graph.on_update(lambda: self.render())

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
            content = self._source.render(self._graph.get(self._current_location))
        elif self._mode[0] == 'help':
            content = self._help_content
        elif self._mode[0] == 'list':
            # TODO
            content = Content()

        if force_put or self._current_content != content:
            self._parent.put_content(content)
        self._current_content = content

    def render_denite(self, context, mode):
        context['is_async'] = False
        if mode == 'symbol':
            return self._source.render_denite(self._graph.get(self._current_location), context)
        elif mode == 'list':
            # TODO
            return []

    def get_at_current_location(self):
        return self._graph.get(self._current_location)

    def update_location(self, location):
        self._current_location = location
        self._graph.require_at_location(location)
        self.render()

    def get_link(self, line, col):
        if(self._current_content is None):
            return ""

        for link in self._current_content.links():
            if(link.line == line and link.start_col <= col and (link.end_col == -1 or link.end_col >= col)):
                return str(link.target)

        return ""

    def get_first_reference(self, reference_name):
        wrapper = self._graph.get(self._current_location)
        if(wrapper is None):
            return ""

        refs = wrapper.source_of[reference_name]
        if(not refs.is_loaded()):
            return ""

        return str(refs.get()[0].location) if len(refs.get()) > 0 else ""

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




