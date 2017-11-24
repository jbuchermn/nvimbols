import os
from threading import Lock, Timer

from nvimbols.util import log, on_error
from nvimbols.graph import SymbolsGraph


class NVimbols:
    def __init__(self, vim, context, source):
        self._vim = vim
        self._context = context
        self._source = source
        self._graph = SymbolsGraph(self._source, self)

        self._current_location = None
        self._current_content = None
        self._rendered_content = None

        self._vim_lock = Lock()

    def _put_content(self):
        def action():
            """
            Do NOT lock inside threadsafe_call. This causes deadlocks for some reason
            """
            if self._vim_lock.acquire(False):
                try:
                    if self._rendered_content == self._current_content:
                        return

                    buf = None
                    window_name = self._vim.call("nvimbols#window_name")
                    for b in self._vim.buffers:
                        if b.name.endswith(window_name):
                            buf = b
                            break

                    if buf is not None:
                        buf.api.set_option('modifiable', True)

                        buf[:] = self._current_content.raw()
                        for highlight in self._current_content.highlights():
                            buf.add_highlight(highlight.name, highlight.line - 1, highlight.start_col - 1, highlight.end_col - 1 if highlight.end_col >= 1 else -1, -1)

                        buf.api.set_option('modifiable', False)

                    self._rendered_content = self._current_content
                finally:
                    self._vim_lock.release()
            else:
                Timer(1., NVimbols._put_content, args=[self]).start()

        self._vim.session.threadsafe_call(action)

    def render(self):
        content = self._source.render_location(self._graph.get_location(self._current_location))
        self._current_content = content
        self._put_content()

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




