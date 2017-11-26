import os

from nvimbols.util import log, on_error
from nvimbols.graph import SymbolsGraph


class NVimbols:
    def __init__(self, parent, source):
        self._parent = parent
        self._source = source
        self.filetypes = source.filetypes
        self._graph = SymbolsGraph(self._source, self)

        self._current_location = None
        self._current_content = None

    def render(self, force_put=False):
        content = self._source.render_location(self._graph.get_location(self._current_location))
        if force_put or self._current_content != content:
            self._parent.put_content(content)
        self._current_content = content

    def clear(self):
        self._graph.clear()
        self.update_location(self._current_location)

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




