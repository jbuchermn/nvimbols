import os
from threading import Lock

from nvimbols.util import log, on_error
from nvimbols.symbol import SymbolLocation
from nvimbols.content import Content, Wrapper, Highlight, Link
from nvimbols.async import JobQueue
from nvimbols.graph import SymbolsGraph


class NVimbols:
    def __init__(self, vim, context, source):
        self._vim = vim
        self._context = context
        self._source = source
        self._graph = SymbolsGraph(self._source)

        self._current_symbol = None
        self._current_content = None

        self._lock = Lock()
        self._job_queue = JobQueue()

    def _render(self):
        content = Content()

        if self._current_symbol is None:
            content += "No symbol"
        else:
            content += Wrapper("Symbol: ", Highlight('Statement', self._current_symbol.name), "\n")
            for d in self._current_symbol.data:
                content += Wrapper("    %s: " % d, Highlight('Type', self._current_symbol.data[d]), "\n")

            for ref in self._graph.references:
                if(len(self._current_symbol.source_of[ref.name]) > 0):
                    content += Highlight('Title', "\n  ----  " + ref.display_targets + "  ----  \n")
                    for s in self._current_symbol.source_of[ref.name]:
                        content += Link(s.location, Highlight('Type', "%s:%i\n" % (os.path.basename(s.location.filename), s.location.start_line)))

                if(len(self._current_symbol.target_of[ref.name]) > 0):
                    content += Highlight('Title', "\n  ----  " + ref.display_sources + "  ----  \n")
                    for s in self._current_symbol.target_of[ref.name]:
                        content += Link(s.location, Highlight('Type', "%s:%i\n" % (os.path.basename(s.location.filename), s.location.start_line)))

        return content

    def _update_symbol(self, symbol):
        """
        Will be called by the JobQueue, i. e. in a new thread.
        """
        with self._lock:
            if(self._current_symbol != symbol):
                self._current_symbol = symbol
                self._current_content = self._render()
                self._vim.session.threadsafe_call(lambda: self._vim.call("nvimbols#update_symbol"))

    def update_location(self, location):
        with self._lock:
            self._job_queue.add_job(
                lambda: self._graph.symbol_at_location(location),
                lambda symbol, err: self._update_symbol(symbol) if err is None else on_error(self._vim, err)
            )

    def render(self, buf):
        self._job_queue.join()
        with self._lock:
            if(self._current_content is None):
                return

            buf.api.set_option('modifiable', True)

            buf[:] = self._current_content.raw()
            for highlight in self._current_content.highlights():
                buf.add_highlight(highlight.name, highlight.line - 1, highlight.start_col - 1, highlight.end_col - 1 if highlight.end_col >= 1 else -1 , -1)

            buf.api.set_option('modifiable', False)

    def get_link(self, line, col):
        self._job_queue.join()
        with self._lock:
            if(self._current_content is None):
                return ""

            for link in self._current_content.links():
                if(link.line == line and link.start_col <= col and (link.end_col == -1 or link.end_col >= col)):
                    return str(link.target)

            return ""

    def get_first_reference(self, reference_name):
        self._job_queue.join()
        with self._lock:
            if(self._current_symbol is None):
                return ""
            for r in self._current_symbol.source_of:
                if r == reference_name:
                    return str(self._current_symbol.source_of[r][0].location) if len(self._current_symbol.source_of[r]) > 0 else ""

        return ""




